import pandas as pd
import time
from .base_strategy import BaseStrategy
import logging


class MACDStrategy:
    def __init__(self, client, symbol, short_window, long_window, signal_window, stop_loss, take_profit):
        self.client = client
        self.symbol = symbol
        self.short_window = short_window
        self.long_window = long_window
        self.signal_window = signal_window
        self.stop_loss = stop_loss
        self.take_profit = take_profit

    def analyze(self):
        # Pseudo-code example for analyzing MACD and generating trade signals
        macd, signal_line = self.calculate_macd()
        logging.info(f"MACD value: {macd}, Signal line value: {signal_line}")

        if macd > signal_line:
            return 'buy'
        elif macd < signal_line:
            return 'sell'
        return None

    def calculate_macd(self):
        # Implement the logic to calculate MACD using the client and symbol
        # Fetch historical price data, compute MACD and signal line
        return 1, 0.5  # Return mock MACD and signal line values for demonstration


    def _convert_to_dataframe(self, data):
        print(f"MACDStrategy - Data passed to DataFrame: {data[:5]} (showing first 5 rows)")
        print(f"MACDStrategy - Number of columns in data: {len(data[0])} (expected 6)")
        # If there are more than 6 columns, take only the first 6
        if len(data[0]) > 6:
            data = [row[:6] for row in data]
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'close', 'high', 'low', 'volume'])
        print("MACDStrategy - DataFrame created successfully!")
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('timestamp', inplace=True)
        df = df.astype(float)
        return df

    # def calculate_macd(self, close_prices):
    #     short_ema = close_prices.ewm(span=self.short_window, adjust=False).mean()
    #     long_ema = close_prices.ewm(span=self.long_window, adjust=False).mean()
    #     macd = short_ema - long_ema
    #     signal = macd.ewm(span=self.signal_window, adjust=False).mean()
    #     return macd, signal

    def should_buy(self, ohlcv_data):
        df = self._convert_to_dataframe(ohlcv_data)
        df['macd'], df['signal'] = self.calculate_macd(df['close'])
        return df['macd'].iloc[-1] > df['signal'].iloc[-1] and df['macd'].iloc[-2] <= df['signal'].iloc[-2]

    def should_sell(self, ohlcv_data):
        df = self._convert_to_dataframe(ohlcv_data)
        df['macd'], df['signal'] = self.calculate_macd(df['close'])
        return df['macd'].iloc[-1] < df['signal'].iloc[-1] and df['macd'].iloc[-2] >= df['signal'].iloc[-2]

    def execute_stop_loss_take_profit(self, current_price):
        if self.position:
            entry_price = self.position['price']
            if current_price <= entry_price * (1 - self.stop_loss):
                print("Stop-Loss hit: Executing Sell Order")
                self.client.place_order(symbol=self.symbol, side='sell', price=current_price,
                                        size=self.position['size'])
                self.position = None  # Reset position
            elif current_price >= entry_price * (1 + self.take_profit):
                print("Take-Profit hit: Executing Sell Order")
                self.client.place_order(symbol=self.symbol, side='sell', price=current_price,
                                        size=self.position['size'])
                self.position = None  # Reset position

    def execute(self):
        end_time = int(time.time())
        start_time = end_time - (60 * 60 * 24 * 30)  # Fetch last 30 days of data
        ohlcv_data = self.client.get_historical_ohlcv(self.symbol, start_time, end_time)['data']

        current_price = float(ohlcv_data[-1][2])  # Close price of the last candle
        order_size = 0.001  # Example size

        if self.position:
            self.execute_stop_loss_take_profit(current_price)

        if not self.position and self.should_buy(ohlcv_data):
            print("MACD crossover above signal line: Executing Buy Order")
            self.client.place_order(symbol=self.symbol, side='buy', price=current_price, size=order_size)
            self.position = {'price': current_price, 'size': order_size}
        elif self.position and self.should_sell(ohlcv_data):
            print("MACD crossover below signal line: Executing Sell Order")
            self.client.place_order(symbol=self.symbol, side='sell', price=current_price, size=order_size)
            self.position = None
