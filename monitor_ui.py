import sys
import os
import tkinter as tk
import logging
from trading_bot import TradingBot
from kucoin_client import KuCoinClient  # Replace with the correct module path

print("Current directory:", os.getcwd())
print("Python search path:", sys.path)
import settings  # Ensure this import works


class TradingBotUI:
    def __init__(self, master, trading_bot):
        self.master = master
        self.trading_bot = trading_bot
        master.title("Trading Bot Monitor")

        self.label = tk.Label(master, text="Trading Bot Status")
        self.label.pack()

        self.strategies_label = tk.Label(master, text="Strategies:")
        self.strategies_label.pack()

        self.strategies_text = tk.Text(master, height=10, width=50)
        self.strategies_text.pack()

        self.trades_label = tk.Label(master, text="Recent Trades:")
        self.trades_label.pack()

        self.trades_text = tk.Text(master, height=10, width=50)
        self.trades_text.pack()

        self.position_label = tk.Label(master, text="Current Positions:")
        self.position_label.pack()

        self.position_text = tk.Text(master, height=10, width=50)
        self.position_text.pack()

        self.balance_label = tk.Label(master, text="Available Balance:")
        self.balance_label.pack()

        self.balance_text = tk.Text(master, height=10, width=50)
        self.balance_text.pack()

        self.trading_account_label = tk.Label(master, text="Trading Account Balance:")
        self.trading_account_label.pack()

        self.trading_account_text = tk.Text(master, height=10, width=50)
        self.trading_account_text.pack()

        self.refresh_button = tk.Button(master, text="Refresh", command=self.refresh_data)
        self.refresh_button.pack()

        self.refresh_data()

        # Set up periodic refresh
        self.schedule_refresh()

    def schedule_refresh(self):
        self.master.after(60000, self.refresh_data)  # Refresh every 60 seconds

    def refresh_data(self):
        logging.info("Refreshing data...")

        strategies_info = self.trading_bot.get_strategies_info()
        recent_trades_info = self.trading_bot.get_recent_trades_info()
        current_positions_info = self.trading_bot.get_current_position_info()
        balance_info = self.trading_bot.get_balance()
        trading_account_balance = self.trading_bot.get_trading_account_balance()
        account_info = self.trading_bot.get_account()

        logging.info("Strategies Info: %s", strategies_info)
        logging.info("Recent Trades Info: %s", recent_trades_info)
        logging.info("Current Positions Info: %s", current_positions_info)
        logging.info("Balance Info: %s", balance_info)
        logging.info("Trading Account Balance: %s", trading_account_balance)
        logging.info("Account Info: %s", account_info)

        self.strategies_text.delete('1.0', tk.END)
        self.strategies_text.insert(tk.END, strategies_info)

        self.trades_text.delete('1.0', tk.END)
        self.trades_text.insert(tk.END, recent_trades_info)

        self.position_text.delete('1.0', tk.END)
        self.position_text.insert(tk.END, current_positions_info)

        self.balance_text.delete('1.0', tk.END)
        balance_display = "\n\n".join([
            f"{account_type}:\n" + "\n".join(balances) for account_type, balances in balance_info.items()
        ])
        self.balance_text.insert(tk.END, balance_display)

        self.trading_account_text.delete('1.0', tk.END)
        trading_account_display = "\n".join([
            f"{balance['currency']}: {balance['balance']}" for balance in trading_account_balance
        ])
        self.trading_account_text.insert(tk.END, trading_account_display)

        self.schedule_refresh()


# This should be at the end of the monitor_ui.py file
if __name__ == "__main__":
    root = tk.Tk()
    client = KuCoinClient(api_key=settings.API_KEY, api_secret=settings.API_SECRET,
                          api_passphrase=settings.API_PASSPHRASE)
    bot = TradingBot(client, 'ETH-USDT')
    trading_bot_ui = TradingBotUI(root, bot)
    root.mainloop()
