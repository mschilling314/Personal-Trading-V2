import backtesting
import random


class CoinFlip(backtesting.Strategy):
    """
    Flips a coin.  If it's heads, we buy.  If not, we sell.
    """
    def init(self):
        print("CoinFlipped.")


    def next(self):
        if random.random() < 0.5:
            self.buy()
        else:
            self.sell