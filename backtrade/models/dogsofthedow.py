import backtrader
import heapq

class Dogs(backtrader.Strategy):
    def init(self):
        pass

    def next(self):
        if self.first_trading_day():
            # calculate dividend yields for Dow 30
            yields = {}
            for data in self.datas:
                ticker_name = data._name
                yields[ticker_name] = self.calculate_dividend_yield(data)
                
            # purchase 10 highest dividend yields
            stocks_to_buy = self.find_highest_dividend_yields(yields=yields)
            self.rebalance_holdings(stocks_to_buy=stocks_to_buy)
            


    def first_trading_day(self) -> bool:
        if len(self.data) < 2:
            return True
        today = self.data.datetime.date(0)
        yesterday = self.data.datetime.date(-1)
        return yesterday.year != today.year



    def calculate_dividend_yield(self, data):
        # formula is annual_dividend_per_share / current_market_price_per_share * 100
        # will only ever be called first market session of a new year, so start at -1
        year = data.datetime.date(-1).year
        index = -1
        dividend = 0
        while data.datetime.date(index).year == year:
            dividend += data.dividends[index]
            index -= 1

        current_price = data.open[0]
        dividend_yield = dividend / current_price * 100 if current_price > 0 else 0
        return dividend_yield


    def find_highest_dividend_yields(self, yields: dict, n: int=5) -> list:
        heap = [(value, key) for key, value in yields.items()]
        heapq.heapify(heap)

        n_largest = heapq.nlargest(n=n, iterable=heap)
        result = []
        for element in n_largest:
            result.append(element[1])
        
        return result
    
    def rebalance_holdings(self, stocks_to_buy: list[str]) -> None:
        for data in self.datas:
            if data._name in stocks_to_buy:
                continue
            position = self.getposition(data)
            if position.size > 0:
                self.sell(data=data, size=position.size)
        money_to_allocate = 0.1 * self.broker.get_cash()
        for stock in stocks_to_buy:
            data_feed = self.getdatabyname(stock)
            sizzle = money_to_allocate / data_feed.close[0]
            posn = self.getposition(data_feed)
            size_to_buy = sizzle - posn.size * posn.price
            if not size_to_buy:
                continue
            self.buy(data_feed, size=sizzle)