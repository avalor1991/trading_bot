from kucoin_api.client import KuCoinClient
from strategies.strategy_rsi import RSIStrategy
from strategies.strategy_macd import MACDStrategy
from trading_bot import TradingBot


def test_run():
    client = KuCoinClient()
    symbol = 'ETH-USDT'

    bot = TradingBot(client, symbol)

    rsi_strategy = RSIStrategy(client, symbol, rsi_period=14, rsi_overbought=70, rsi_oversold=30, stop_loss=0.02,
                               take_profit=0.05)
    macd_strategy = MACDStrategy(client, symbol, short_window=12, long_window=26, signal_window=9, stop_loss=0.02,
                                 take_profit=0.05)

    bot.add_strategy(rsi_strategy)
    bot.add_strategy(macd_strategy)

    # Run the bot
    bot.run()

    # Verify the recent trades
    print("Recent Trades Info (Test):")
    print(bot.get_recent_trades_info())

    # Verify the current position
    print("Current Position Info (Test):")
    print(bot.get_current_position_info())


if __name__ == "__main__":
    test_run()
