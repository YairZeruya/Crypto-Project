from datetime import datetime
import ccxt
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from binance.client import Client
from strategy import RSI_Strategy, EMA_Strategy, MACD_Strategy
from helper import klines_extended
from backtesting import Backtest

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

api_key = 'b7K72xGGe7uB1ZPQxjsfTZ6keY3kuZAkGI73RKylAB1qDcStuezY40VajCovytvP'
api_secret = 'TQZkqjPRuQZUquOH8DwUN3D9MPC959IM7XapJpKDUv7YFIGkH8tBp0jgt5cMmBEK'

# Mapping strategy names to actual strategy classes
strategy_mapping = {
    "RSI_Strategy": RSI_Strategy,
    "EMA_Strategy": EMA_Strategy,
    "MACD_Strategy": MACD_Strategy
}


# init
@app.route('/binance')
@cross_origin()
def get_coins_binance():
    client = Client(api_key, api_secret, tld= "com", testnet=True)

    client.API_URL = "https://testnet.binance.vision/api"
    coins = client.get_all_tickers()
    return coins


@app.route('/binance/<coin>')
def get_coin_data(coin):
    exchange = ccxt.binance()
    symbol = f"{coin.upper()}/USDT"

    end_date = exchange.milliseconds()  # current timestamp in milliseconds
    # Define the start date based on the timeframe
    timeframe = request.args.get('timeframe', default='1d')  # Default to daily
    if timeframe == '1d':
        start_date = end_date - 365 * 24 * 60 * 60 * 1000  # One year
    elif timeframe == '1w':
        start_date = end_date - 365 * 24 * 60 * 60 * 1000  # One years
    elif timeframe == '1M':
        start_date = end_date - 5 * 365 * 24 * 60 * 60 * 1000  # Five years

    # Fetch OHLCV (Open, High, Low, Close, Volume) data for the symbol and timeframe
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1d', since=start_date, limit=None)

    # Prepare the data to be returned
    historical_prices = []
    for data in ohlcv:
        timestamp = datetime.utcfromtimestamp(data[0] / 1000).strftime('%Y-%m-%d')
        price = data[4]  # Closing price
        historical_prices.append({"date": timestamp, "price": price})

    # Return the historical prices as JSON
    return jsonify({"coin": coin.upper(), "historical_prices": historical_prices})


@app.route('/strategies')
def get_strategies():
    # Debug print to verify endpoint is being accessed
    print("Accessing /strategies endpoint")
    return jsonify(list(strategy_mapping.keys()))


@app.route('/backtest/<strategy_name>')
def run_backtest_all(strategy_name):
    try:
        # Validate the strategy
        if strategy_name not in strategy_mapping:
            return jsonify({"error": f"Strategy '{strategy_name}' not found"}), 400

        strategy = strategy_mapping[strategy_name]

        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT", "SOLUSDT", "DOTUSDT", "DOGEUSDT", "LTCUSDT", "UNIUSDT",
                   "LINKUSDT", "BCHUSDT", "XLMUSDT", "MATICUSDT", "VETUSDT", "TRXUSDT", "FTTUSDT", "AAVEUSDT", "FILUSDT", "ALGOUSDT",
                   "EGLDUSDT", "XMRUSDT", "IOTAUSDT", "KSMUSDT", "CAKEUSDT", "SUSHIUSDT", "COMPUSDT", "ZILUSDT", "RUNEUSDT", "AVAXUSDT",
                   "HBARUSDT", "ENJUSDT", "CHZUSDT", "BATUSDT", "ZRXUSDT", "SNXUSDT", "LUNAUSDT", "NEOUSDT", "ATOMUSDT", "ICPUSDT",
                   "HNTUSDT", "YFIUSDT", "1INCHUSDT", "GRTUSDT", "MKRUSDT", "UMAUSDT", "CELUSDT", "QTUMUSDT", "OMGUSDT", "FETUSDT"]

        timeframe = request.args.get('timeframe', default='1h')
        interval = int(request.args.get('interval', default=30))
        tp = 0.03
        sl = 0.02

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

        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/backtest/<symbol>')
def run_backtest(symbol):
    # Extracting timeframe and interval from query parameters with default values
    timeframe = request.args.get('timeframe', default='1h')
    interval = int(request.args.get('interval', default=30))
    tp = 0.03
    sl = 0.02

    kl = klines_extended(symbol, timeframe, interval)
    bt = Backtest(kl, RSI_Strategy, cash=1000000, margin=1/10, commission=0.0007)
    stats = bt.run()

    result = {
        "currency": symbol,
        "return": stats['Return [%]'],
        "bot_name": "RSI Bot",
        "description": "A simple RSI-based trading bot that buys when RSI<30 and sells when RSI>70.",
        "timeframe": timeframe,
        "duration": str(stats["Duration"]),
        "Buy and Hold Return": stats["Buy & Hold Return [%]"],
        "Trades": stats["# Trades"],
        "Win Rate": stats["Win Rate [%]"],
    }

    return jsonify(result)


@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
   app.run(host="0.0.0.0",port=5586)