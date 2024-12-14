import backtesting


class DowDogs(backtesting.Strategy):
    """
    Dogs of the Dow is a strategy wherein the 10 stocks in the Dow with the highest dividend yield (dividends/stock price) at the end of December
    are purchased on the first January market open in equal or weighted amounts, with sales of the previous year's picks being done at the same
    time.
    """
    def init(self):
        self.years_traded = []

    def next(self):
        current_date = self.data.index[-1]

        if current_date.year not in self.years_traded:
            self.years_traded.append(current_date.year)
            