import json
import logging

class TradingBot:
    def __init__(self, client, symbol):
        self.client = client
        self.symbol = symbol
        self.strategies = []
        self.position = None
        self.recent_trades = []

        logging.info(f"TradingBot initialized for symbol: {self.symbol}")

    def add_strategy(self, strategy):
        self.strategies.append(strategy)
        logging.info(f"Added strategy: {strategy.__class__.__name__}")

    def remove_strategy(self, strategy):
        self.strategies.remove(strategy)
        logging.info(f"Removed strategy: {strategy.__class__.__name__}")

    def execute_trade(self, trade_signal):
        logging.info(f"Executing trade with signal: {trade_signal}")
        if trade_signal == 'buy':
            self._buy()
        elif trade_signal == 'sell':
            self._sell()

    def _buy(self):
        if self.position is None:
            price = self._get_current_price()
            amount = 1  # Define your logic for buying amount here
            self.position = {'type': 'long', 'price': price, 'amount': amount}
            logging.info(
                f"Executed BUY trade at price: {self.position['price']} with amount: {self.position['amount']}")
            self.recent_trades.append(f"Bought {self.position['amount']} at {self.position['price']}")
        else:
            logging.warning("Attempted BUY but already in a position!")

    def _sell(self):
        if self.position is not None:
            sell_price = self._get_current_price()
            logging.info(f"Current price for SELL: {sell_price}")
            logging.info(f"Executed SELL trade at price: {sell_price} with amount: {self.position['amount']}")
            self.recent_trades.append(f"Sold {self.position['amount']} at {sell_price}")
            self.position = None
        else:
            logging.warning("Attempted SELL but not in a position!")

    def _get_current_price(self):
        ticker_info = self.client.get_ticker(self.symbol)
        price = float(ticker_info['price'])
        logging.info(f"Fetched current price: {price}")
        return price

    def get_balance(self):
        account_balances = self.client.get_balance()
        logging.info(f"Fetched balance information: {account_balances}")
        return account_balances

    def get_account(self):
        account_info = self.client.get_account()
        logging.info(f"Account information: {account_info}")
        return account_info

    def get_trading_account_balance(self):
        balances = self.get_balance()

        logging.info(f"Balances: {balances}")

        if isinstance(balances, str):
            balances = json.loads(balances)

        balance_keys = balances.keys() if hasattr(balances, 'keys') else []
        logging.info(f"Balances keys: {balance_keys}")

        if 'data' in balances:
            trading_account_balance = [balance for balance in balances['data'] if
                                       'type' in balance and balance['type'] == 'trade']
        else:
            trading_account_balance = [balance for balance in balances if
                                       'type' in balance and balance['type'] == 'trade']

        logging.info(f"Trading Account Balance: {trading_account_balance}")
        return trading_account_balance

    def run(self):
        while True:
            logging.info("Running trading strategies...")
            for strategy in self.strategies:
                trade_signal = strategy.analyze()
                logging.info(f"Strategy {strategy.__class__.__name__} generated signal: {trade_signal}")
                if trade_signal:
                    logging.info(f"Trade signal received: {trade_signal}")
                    self.execute_trade(trade_signal)

            logging.info("Sleeping for 60 seconds...")
            time.sleep(60)

    def get_strategies_info(self):
        return "\n".join([strategy.__class__.__name__ for strategy in self.strategies])

    def get_recent_trades_info(self):
        return "\n".join(self.recent_trades)

    def get_current_position_info(self):
        if not self.position:
            return "No Position"
        return f"Position: {self.position['type']} at {self.position['price']} with amount {self.position['amount']}"
