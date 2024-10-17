import datetime
import backtesting


BUY_TIMES = ["9:30"]#, "10:30", "11:30", "12:30", "13:30", "14:30"]
for i in range(len(BUY_TIMES)):
    t = BUY_TIMES[i].split(":")
    BUY_TIMES[i] = datetime.time(hour=int(t[0]), minute=int(t[1]), second=0)

SELL_TIMES = ["15:55"]#, "10:55", "11:55", "12:55", "13:55", "14:55"]
for i in range(len(SELL_TIMES)):
    t = SELL_TIMES[i].split(":")
    SELL_TIMES[i] = datetime.time(hour=int(t[0]), minute=int(t[1]), second=0)

PROFIT_CAPTURE_PERCENT = 0.03
LOSS_AVERSION_PERCENT = 0.01


class VolatilityShortStrategy(backtesting.Strategy):
    buy_price = 0

    def init(self):
        # self.price = self.I(self.data.Close)
        # self.time = self.I(self.data.index.time())
        pass


    def next(self):
        self.current_time = self.data.index[-1].time()
        self.current_price = self.data.Close[-1]
        # if self.position.size != 0:
        #     print(self.position.size)
        self.buy_or_sell_short()

    
    def buy_or_sell_short(self) -> None:
        if self.current_time in BUY_TIMES and self.data.Close[-1] > self.data.Close[-2]:
            self.buy_price = self.current_price
            # print(f"Buy Triggered {self.data.index[-1]}")
            self.sell()
        elif self.position.size < 0 and self.current_price > (1 + LOSS_AVERSION_PERCENT) * self.buy_price:
            # Mitigates loss
            # print(f"Sell Triggered to mitigate loss at {self.data.index[-1]}")
            self.buy()
        elif self.position.size < 0 and  self.current_price <= (1 - PROFIT_CAPTURE_PERCENT) * self.buy_price:
            # Captures some profit
            # print(f"Sell Triggered to capture profit at {self.data.index[-1]}")
            self.buy()
        elif self.position.size < 0 and  self.current_time in SELL_TIMES: #== datetime.time(hour=15, minute=55, second=0):
            # print(f"Sell Triggered {self.data.index[-1]}")
            self.buy()