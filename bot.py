import os
import time
from binance.client import Client
from binance.enums import *
import requests

api_key = 'A8jFlxDhcYtyLdm3eY9uVRyVcoGm9N2a9ZP9rtBNxeP0hCvyYMVcb7n23DN7vJYG'
api_secret = 'Ywdc7nDJJE0FnjrrbCicg580LzX8kzpWFSLy0DMXTUkPQzi6Dksez0ngXwKmoDyp'

client = Client(api_key, api_secret)

def get_rsi(symbol, period='1h', interval='1m', window=14):
    klines = client.get_historical_klines(symbol, interval, period)
    close_prices = [float(entry[4]) for entry in klines]
    deltas = [close_prices[i] - close_prices[i - 1] for i in range(1, len(close_prices))]
    gain = sum(delta for delta in deltas if delta > 0) / window
    loss = -sum(delta for delta in deltas if delta < 0) / window
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def get_minimum_order_size(symbol):
    url = "https://api.binance.com/api/v3/exchangeInfo"
    response = requests.get(url)
    if response.status_code == 200:
        exchange_info = response.json()
        for symbol_info in exchange_info["symbols"]:
            if symbol_info["symbol"] == symbol:
                return float(symbol_info["filters"][1]["minQty"])  # Filter index 1 contains LOT_SIZE information
        return None  # Symbol not found
    else:
        print("Failed to retrieve exchange info:", response.status_code)
        return None

def main():
    symbol = 'NEOUSDT'
    minimum_order_size = get_minimum_order_size(symbol)
    if minimum_order_size is not None:
        print(f"Minimum order size for {symbol}: {minimum_order_size}")
    else:
        print(f"Symbol {symbol} not found.")
        return

    rsi = get_rsi(symbol)
    print(f'Current RSI for {symbol}: {rsi}')

    current_price = float(client.get_symbol_ticker(symbol=symbol)['price'])
    # Calculate the minimum notional value required
    min_notional = 10.0  # Example minimum notional value

    # Calculate the quantity based on the minimum order size
    quantity = minimum_order_size

    # Calculate the notional value of the order
    notional_value = current_price * quantity

    print(f"Calculated quantity: {quantity}")
    print(f"Calculated notional value: {notional_value}")

    # Check if the calculated notional value satisfies the minimum notional value requirement
    if notional_value >= min_notional:
        if rsi > 70:
            order = client.create_test_order(
                symbol=symbol,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
            print("SELL order placed")
        elif rsi < 60:
            order = client.create_test_order(
                symbol=symbol,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
            print("BUY order placed")
    else:
        print("Notional value does not satisfy the minimum notional requirement.")

    # You can adjust the sleep time according to your trading frequency
    time.sleep(300)  # 5 minutes


if __name__ == "__main__":
    main()