# tests/test_flask_app.py
import pytest
import requests

@pytest.fixture(scope='module')
def api_url():
    return 'http://localhost:5586'

def test_get_coins_binance(api_url):
    response = requests.get(f'{api_url}/binance')
    assert response.status_code == 200
    coins = response.json()
    assert isinstance(coins, list)

def test_get_coin_data(api_url):
    coin = 'BTC'
    response = requests.get(f'{api_url}/binance/{coin}?timeframe=1d')
    assert response.status_code == 200
    data = response.json()
    assert data['coin'] == coin.upper()
    assert isinstance(data['historical_prices'], list)

def test_get_strategy_descriptions(api_url):
    response = requests.get(f'{api_url}/strategy_descriptions')
    assert response.status_code == 200
    descriptions = response.json()
    assert isinstance(descriptions, dict)

def test_get_strategies(api_url):
    response = requests.get(f'{api_url}/strategies')
    assert response.status_code == 200
    strategies = response.json()
    assert isinstance(strategies, list)

def test_run_backtest_all(api_url):
    strategy_name = 'RSI_Strategy'
    response = requests.get(f'{api_url}/backtest/{strategy_name}')
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)

def test_create_trade(api_url):
    data = {
        "symbol": "BTCUSDT",
        "cost": 1000,
        "start_time": "2023-01-01T17:20",
        "bot_name": "TestBot"
    }
    response = requests.post(f'{api_url}/trade/buy', json=data)
    assert response.status_code == 200
    new_trade = response.json()
    assert isinstance(new_trade, dict)
    assert new_trade['symbol'] == data['symbol']
    assert new_trade['cost'] == data['cost']
    assert new_trade['start_time'] == data['start_time']
    assert new_trade['bot_name'] == data['bot_name']

def test_get_trade_by_id(api_url):
    trade_id = 1
    response = requests.get(f'{api_url}/trade/{trade_id}')
    assert response.status_code == 200
    trade = response.json()
    assert isinstance(trade, dict)
    assert trade['id'] == trade_id

if __name__ == '__main__':
    pytest.main()

