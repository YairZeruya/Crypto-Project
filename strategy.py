import pandas as pd
import ta
from backtesting import Strategy

# Take Profit and Stop Loss. 0.03 means 3%
tp = 0.03
sl = 0.02

# RSI indicator function
def rsi(df, period=14):
    return ta.momentum.RSIIndicator(pd.Series(df), window=period).rsi()

# EMA indicator function
def ema(df, period=200):
    return ta.trend.EMAIndicator(pd.Series(df), window=period).ema_indicator()

# MACD indicator function
def macd(df, fast_period=12, slow_period=26, signal_period=9):
    macd_indicator = ta.trend.MACD(pd.Series(df), window_slow=slow_period, window_fast=fast_period, window_sign=signal_period)
    return macd_indicator.macd(), macd_indicator.macd_signal()

# Define the RSI strategy
class RSI_Strategy(Strategy):
    ema_period = 200
    rsi_period = 14
    description = ("This strategy uses the Relative Strength Index (RSI) indicator. "
                            "The RSI measures the magnitude of recent price changes to evaluate overbought or oversold conditions. "
                            "This strategy buys when RSI is below 30 and sells when RSI is above 70.")

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)

    def init(self):
        price = self.data.Close
        self.rsi = self.I(rsi, self.data.Close, self.rsi_period)

    def next(self):
        price = float(self.data.Close[-1])
        if not self.position and self.rsi[-2] < 30:
            self.buy(size=0.02, tp=(1+tp)*price, sl=(1-sl)*price)
        if not self.position and self.rsi[-2] > 70:
            self.sell(size=0.02, tp=(1-tp)*price, sl=(1+sl)*price)

# Define the EMA strategy
class EMA_Strategy(Strategy):
    ema_period = 200
    description = ("This strategy uses the Exponential Moving Average (EMA) indicator. "
                            "The EMA gives more weight to recent prices, making it more responsive to new information. "
                            "This strategy buys when the price is above the 200-period EMA and sells when the price is below the 200-period EMA.")

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)

    def init(self):
        price = self.data.Close
        self.ema = self.I(ema, self.data.Close, self.ema_period)

    def next(self):
        price = float(self.data.Close[-1])
        if not self.position and price > self.ema[-2]:
            self.buy(size=0.02, tp=(1+tp)*price, sl=(1-sl)*price)
        elif not self.position and price < self.ema[-2]:
            self.sell(size=0.02, tp=(1-tp)*price, sl=(1+sl)*price)

# Define the MACD strategy
class MACD_Strategy(Strategy):
    macd_fast_period = 12
    macd_slow_period = 26
    macd_signal_period = 9
    description = ("This strategy uses the Moving Average Convergence Divergence (MACD) indicator. "
                            "The MACD is a trend-following momentum indicator that shows the relationship between two moving averages of a security’s price. "
                            "This strategy buys when MACD crosses below the signal line and sells when MACD crosses above the signal line.")

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)

    def init(self):
        price = self.data.Close
        self.macd, self.signal = self.I(macd, self.data.Close, self.macd_fast_period, self.macd_slow_period, self.macd_signal_period)

    def next(self):
        price = float(self.data.Close[-1])
        if not self.position:
            if self.macd[-2] > self.signal[-2] and self.macd[-1] < self.signal[-1]:
                self.buy(size=0.02, tp=(1+tp)*price, sl=(1-sl)*price)
            elif self.macd[-2] < self.signal[-2] and self.macd[-1] > self.signal[-1]:
                self.sell(size=0.02, tp=(1-tp)*price, sl=(1+sl)*price)