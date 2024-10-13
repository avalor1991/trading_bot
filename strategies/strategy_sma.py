import pandas as pd
from .base_strategy import BaseStrategy


class SMACrossoverStrategy(BaseStrategy):
    def __init__(self, client, symbol, short_window=40, long_window=100):
        super().__init__(client)
        self.symbol = symbol
        self.short_window = short_window
        self.long_window = long_window

    def _convert_to_dataframe(self, data):
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'close', 'high', 'low', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('timestamp', inplace=True)
        df = df.astype(float)
        return df

    def calculate_sma(self, data, window):
        return data['close'].rolling(window=window).mean()

    def should_buy(self, ohlcv_data):
        df = self._convert_to_dataframe(ohlcv_data)
        df['short_sma'] = self.calculate_sma(df, self.short_window)
        df['long_sma'] = self.calculate_sma(df, self.long_window)

        if df['short_sma'].iloc[-1] > df['long_sma'].iloc[-1] and \
                df['short_sma'].iloc[-2] <= df['long_sma'].iloc[-2]:
            return True
        return False

    def should_sell(self, ohlcv_data):
        df = self._convert_to_dataframe(ohlcv_data)
        df['short_sma'] = self.calculate_sma(df, self.short_window)
        df['long_sma'] = self.calculate_sma(df, self.long_window)

        if df['short_sma'].iloc[-1] < df['long_sma'].iloc[-1] and \
                df['short_sma'].iloc[-2] >= df['long_sma'].iloc[-2]:
            return True
        return False

    def execute(self):
        end_time = int(time.time())
        start_time = end_time - (60 * 60 * 24 * 30)  # Fetch last 30 days of data
        ohlcv_data = self.client.get_historical_ohlcv(self.symbol, start_time, end_time)['data']

        if self.should_buy(ohlcv_data):
            print("Executing Buy Order")
            # Implement buy logic here
        elif self.should_sell(ohlcv_data):
            print("Executing Sell Order")
            # Implement sell logic here
