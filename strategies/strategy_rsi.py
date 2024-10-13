import pandas as pd
import time
from .base_strategy import BaseStrategy
import logging


class RSIStrategy:
    def __init__(self, client, symbol, rsi_period, rsi_overbought, rsi_oversold, stop_loss, take_profit):
        self.client = client
        self.symbol = symbol
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.stop_loss = stop_loss
        self.take_profit = take_profit

    def analyze(self):
        ticker_info = self.client.get_ticker(self.symbol)
        price = float(ticker_info['price'])

        rsi = self.calculate_rsi(price)
        logging.info(f"RSI value: {rsi}")

        if rsi > self.rsi_overbought:
            logging.info("RSI Overbought - Signal to sell")
            return 'sell'
        elif rsi < self.rsi_oversold:
            logging.info("RSI Oversold - Signal to buy")
            return 'buy'

        return None

    def calculate_rsi(self, price):
        # Placeholder code, implement actual RSI calculation here
        return 50  # Example placeholder for RSI calculation



    def _convert_to_dataframe(self, data):
        print(f"RSIStrategy - Data passed to DataFrame: {data[:5]} (showing first 5 rows)")
        print(f"RSIStrategy - Number of columns in data: {len(data[0])} (expected 6)")
        # If there are more than 6 columns, take only the first 6
        if len(data[0]) > 6:
            data = [row[:6] for row in data]
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'close', 'high', 'low', 'volume'])
        print("RSIStrategy - DataFrame created successfully!")
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('timestamp', inplace=True)
        df = df.astype(float)
        return df


    # def calculate_rsi(self, close_prices, period):
    #     delta = close_prices.diff(1)
    #     gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    #     loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    #     rs = gain / loss
    #     rsi = 100 - (100 / (1 + rs))
    #     return rsi

    def should_buy(self, ohlcv_data):
        df = self._convert_to_dataframe(ohlcv_data)
        df['rsi'] = self.calculate_rsi(df['close'], self.rsi_period)
        current_rsi = df['rsi'].iloc[-1]
        return current_rsi < self.rsi_oversold

    def should_sell(self, ohlcv_data):
        df = self._convert_to_dataframe(ohlcv_data)
        df['rsi'] = self.calculate_rsi(df['close'], self.rsi_period)
        current_rsi = df['rsi'].iloc[-1]
        return current_rsi > self.rsi_overbought

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
            print("RSI below 30: Executing Buy Order")
            self.client.place_order(symbol=self.symbol, side='buy', price=current_price, size=order_size)
            self.position = {'price': current_price, 'size': order_size}
        elif self.position and self.should_sell(ohlcv_data):
            print("RSI above 70: Executing Sell Order")
            self.client.place_order(symbol=self.symbol, side='sell', price=current_price, size=order_size)
            self.position = None
