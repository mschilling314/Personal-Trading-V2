import backtrader
import random


class CoinFlip(backtrader.Strategy):
    """
    Flips a coin.  If it's heads, we buy.  If not, we sell.
    """
    def init(self):
        print("CoinFlipped.")


    def next(self):
        print("Flipping a coin.")
        if random.random() < 0.5:
            self.buy()
        else:
            self.sell()