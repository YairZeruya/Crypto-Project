from datetime import datetime
import ccxt
from binance.client import Client
from strategy import RSI_Strategy, EMA_Strategy, MACD_Strategy
from backtesting import Backtest
from helper import klines_extended
from trade import Trade
from db import DB
import requests
from enums import TradeStatus

class AppManager:

    def __init__(self, db_name):
        self.api_key = 'b7K72xGGe7uB1ZPQxjsfTZ6keY3kuZAkGI73RKylAB1qDcStuezY40VajCovytvP'
        self.api_secret = 'TQZkqjPRuQZUquOH8DwUN3D9MPC959IM7XapJpKDUv7YFIGkH8tBp0jgt5cMmBEK'
        self.exchange = ccxt.binance()
        self.strategy_mapping = {
            "RSI_Strategy": {"class": RSI_Strategy, "description": RSI_Strategy.description},
            "EMA_Strategy": {"class": EMA_Strategy, "description": EMA_Strategy.description},
            "MACD_Strategy": {"class": MACD_Strategy, "description": MACD_Strategy.description}
        }
        self.trades: list = []
        self.db = DB(db_name)

    def get_coins_binance(self):
        client = Client(self.api_key, self.api_secret, tld="com", testnet=True)
        client.API_URL = "https://testnet.binance.vision/api"
        return client.get_all_tickers()

    def get_coin_data(self, coin, timeframe):
        symbol = f"{coin.upper()}/USDT"
        end_date = self.exchange.milliseconds()

        if timeframe == '1d':
            start_date = end_date - 365 * 24 * 60 * 60 * 1000 
        elif timeframe == '1w':
            start_date = end_date - 365 * 24 * 60 * 60 * 1000 
        elif timeframe == '1M':
            start_date = end_date - 5 * 365 * 24 * 60 * 60 * 1000
        else:
            raise ValueError("Invalid timeframe provided")

        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe='1d', since=start_date, limit=None)

        historical_prices = []
        for data in ohlcv:
            timestamp = datetime.utcfromtimestamp(data[0] / 1000).strftime('%Y-%m-%d')
            price = data[4]  # Closing price
            historical_prices.append({"date": timestamp, "price": price})

        return {"coin": coin.upper(), "historical_prices": historical_prices}

    def get_strategy_descriptions(self):
        return {
            name: {"name": name, "description": strategy["description"]}
            for name, strategy in self.strategy_mapping.items()
        }

    def get_strategies(self):
        return list(self.strategy_mapping.keys())

    def run_backtest_all(self, strategy_name, timeframe='1h', interval=30):
        try:
            if strategy_name not in self.strategy_mapping:
                raise ValueError(f"Strategy '{strategy_name}' not found")

            strategy = self.strategy_mapping[strategy_name]['class']

            symbols = [
                "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT", "SOLUSDT", "DOTUSDT", "DOGEUSDT", "LTCUSDT", "UNIUSDT",
                "LINKUSDT", "BCHUSDT", "XLMUSDT", "MATICUSDT", "VETUSDT", "TRXUSDT", "FTTUSDT", "AAVEUSDT", "FILUSDT", "ALGOUSDT",
                "EGLDUSDT", "XMRUSDT", "IOTAUSDT", "KSMUSDT", "CAKEUSDT", "SUSHIUSDT", "COMPUSDT", "ZILUSDT", "RUNEUSDT", "AVAXUSDT",
                "HBARUSDT", "ENJUSDT", "CHZUSDT", "BATUSDT", "ZRXUSDT", "SNXUSDT", "LUNAUSDT", "NEOUSDT", "ATOMUSDT", "ICPUSDT",
                "HNTUSDT", "YFIUSDT", "1INCHUSDT", "GRTUSDT", "MKRUSDT", "UMAUSDT", "CELUSDT", "QTUMUSDT", "OMGUSDT", "FETUSDT"
            ]

            results = []
            for symbol in symbols:
                try:
                    kl = klines_extended(symbol, timeframe, interval)
                    bt = Backtest(kl, strategy, cash=1000000, margin=1/10, commission=0.0007)
                    stats = bt.run()

                    result = {
                        "currency": symbol,
                        "return": stats['Return [%]'],
                        "Buy and Hold Return": stats["Buy & Hold Return [%]"],
                        "Trades": stats["# Trades"],
                        "Win Rate": stats["Win Rate [%]"],
                    }
                    results.append(result)
                except Exception as e:
                    results.append({"currency": symbol, "error": str(e)})

            return results
        except Exception as e:
            raise e

    def create_trade(self, symbol: str, cost: int, start_time: str, bot_name: str) -> Trade:
        if self.get_current_balance() < cost:
            raise ValueError("Insufficient balance to create trade")
        
        try:
            start_price = self.get_start_price_from_binance(symbol)
            new_trade = Trade.create_trade(symbol, cost, start_time, bot_name, start_price)
            self.db.save_trade(new_trade, start_price)
            self.update_balance(-cost)  # Deduct cost from balance
            return new_trade
        except Exception as e:
            raise e

    def get_start_price_from_binance(self, symbol):
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            start_price = float(data['price'])
            return start_price
        else:
            raise ValueError(f"Failed to fetch start price for {symbol} from Binance API")

    def get_trade_by_id(self, trade_id):
        try:
            return self.db.get_trade_by_id(trade_id)
        except Exception as e:
            print(f"Error fetching trade by ID: {e}")
            raise e

    def sell_trade(self, trade_id, end_time):
        trade = self.db.get_trade_by_id(trade_id)
        if trade:
            end_price = self.get_start_price_from_binance(trade.get('symbol'))
            start_price = trade.get('start_price')
            cost = trade.get('cost')

            # Calculate return value
            return_value = ((end_price - start_price) / start_price) * cost
            
            self.db.update_trade(trade_id, end_price, end_time, return_value)
            updated_trade = self.db.get_trade_by_id(trade_id)
            
            create_trade = Trade(
                updated_trade.get('id'),
                updated_trade.get('symbol'),
                updated_trade.get('cost'),
                updated_trade.get('start_time'),
                updated_trade.get('strategy'),
                updated_trade.get('start_price'),
            )
            create_trade.end_time = updated_trade.get('end_time')
            create_trade.profit = updated_trade.get('return')
            create_trade.status = TradeStatus.close.value
            create_trade.end_price = updated_trade.get('end_price')

            # Update balance after selling the trade
            self.update_balance(create_trade.profit + create_trade.cost)

            print(f'createdtrade : {create_trade.to_dict()}')
            return create_trade
        else:
            raise ValueError(f"Trade with ID {trade_id} not found")

    def update_balance(self, amount):
        current_balance = self.db.get_balance()
        updated_balance = current_balance + amount
        self.db.save_balance(updated_balance)

    def get_current_balance(self):
        return self.db.get_balance()

    def get_all_trades(self):
        try:
            return self.db.get_all_trades()
        except Exception as e:
            print(f"Error fetching all trades: {e}")
            raise e
