# tests/test_app_manager.py
import pytest
from unittest.mock import patch, Mock
from app_manager import AppManager, Trade

@pytest.fixture
def app_manager():
    return AppManager(db_name='test.db')  # Use a different test database here

def test_get_coins_binance(app_manager):
    with patch('app_manager.Client') as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.get_all_tickers.return_value = [{'symbol': 'BTCUSDT'}, {'symbol': 'ETHUSDT'}]
        
        coins = app_manager.get_coins_binance()
        assert coins == [{'symbol': 'BTCUSDT'}, {'symbol': 'ETHUSDT'}]

def test_get_coin_data(app_manager):
    coin = 'btc'
    timeframe = '1d'
    with patch.object(app_manager.exchange, 'fetch_ohlcv') as mock_fetch_ohlcv:
        mock_fetch_ohlcv.return_value = [
            (1624262400000, 35700.0, 36500.0, 35000.0, 36000.0, 1000.0)
        ]
        
        data = app_manager.get_coin_data(coin, timeframe)
        assert data['coin'] == 'BTC'
        assert len(data['historical_prices']) == 1
        assert data['historical_prices'][0]['price'] == 36000.0

def test_run_backtest_all(app_manager):
    strategy_name = 'RSI_Strategy'
    with patch('app_manager.Backtest') as MockBacktest:
        mock_instance = MockBacktest.return_value
        mock_instance.run.return_value = {
            'Return [%]': 10.0,
            'Buy & Hold Return [%]': 5.0,
            '# Trades': 50,
            'Win Rate [%]': 60.0
        }
        
        results = app_manager.run_backtest_all(strategy_name)
        assert len(results) > 0
        assert 'currency' in results[0]
        assert 'return' in results[0]
        assert 'Buy and Hold Return' in results[0]
        assert 'Trades' in results[0]
        assert 'Win Rate' in results[0]

def test_create_trade(app_manager):
    symbol = 'BTCUSDT'
    cost = 1000
    start_time = '2023-01-01'
    bot_name = 'TestBot'

    with patch.object(app_manager, 'get_start_price_from_binance') as mock_get_start_price:
        mock_get_start_price.return_value = 35000.0

        new_trade = app_manager.create_trade(symbol, cost, start_time, bot_name)
        assert isinstance(new_trade, Trade)
        assert new_trade.symbol == symbol
        assert new_trade.cost == cost
        assert new_trade.start_time == start_time
        assert new_trade.bot_name == bot_name
        assert new_trade.start_price == 35000.0

def test_get_start_price_from_binance(app_manager):
    symbol = 'BTCUSDT'
    with patch('app_manager.requests.get') as mock_requests_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'price': '35000.0'}
        mock_requests_get.return_value = mock_response

        start_price = app_manager.get_start_price_from_binance(symbol)
        assert start_price == 35000.0

def test_get_trade_by_id(app_manager):
    trade_id = 1
    expected_trade_data = {
        "id": trade_id,
        "symbol": "BTCUSDT",
        "strategy": "RSI_Strategy",
        "start_time": "2023-01-01",
        "end_time": None,
        "cost": 1000,
        "start_price": 35000.0,
        "end_price": None,
        "return": 0.0
    }
    with patch.object(app_manager.db, 'get_trade_by_id') as mock_get_trade_by_id:
        mock_get_trade_by_id.return_value = expected_trade_data

        trade = app_manager.get_trade_by_id(trade_id)
        assert trade.symbol == expected_trade_data["symbol"]
        assert trade.cost == expected_trade_data["cost"]
        assert trade.start_time == expected_trade_data["start_time"]
        assert trade.bot_name == expected_trade_data["strategy"]
        assert trade.start_price == expected_trade_data["start_price"]

if __name__ == '__main__':
    pytest.main()

