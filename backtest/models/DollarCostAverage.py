import math
import backtesting
import logging


logging.basicConfig(
    level=logging.INFO,
    filename='logs/DCArun.log',
    filemode='w',
    format='%(message)s'
)


class DollarCostAverage(backtesting.Strategy):
    """
    Strategy does a DCA on a bi-weekly basis on Tuesdays, to simulate paychecks hitting Fidelity after payday.
    """
    amount_to_invest = 1000

    def init(self):
        # print("Doing DCA.")
        self.bought_last_week = False
        

    def next(self):
        current_date = self.data.index[-1]

        if current_date.dayofweek == 1:
            if not self.bought_last_week:
                logging.info(f"Position on {current_date}: {self.position.size}\n\tValue of portfolio: {self.data.Close[-1]*self.position.size}")
                sizzle = math.floor(self.amount_to_invest/self.data.Close[-1]) + self.position.size
                if self.position.size > 0:
                    self.sell(size=self.position.size)
                # print(f"The size given is {sizzle}, as the closing price was {self.data.Close[-1]}")
                if sizzle > 0:
                    self.buy(size=sizzle)
                self.bought_last_week = True
            else:
                self.bought_last_week = False