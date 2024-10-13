class BaseStrategy:
    def __init__(self, client):
        self.client = client

    def should_buy(self):
        raise NotImplementedError("Should implement should_buy method")

    def should_sell(self):
        raise NotImplementedError("Should implement should_sell method")

    def execute(self):
        if self.should_buy():
            print("Executing Buy Order")
            # Implement buy logic here
        elif self.should_sell():
            print("Executing Sell Order")
            # Implement sell logic here
