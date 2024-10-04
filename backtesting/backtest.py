import os
import time
import backtesting
import requests
import yfinance as yf
import pandas as pd
import datetime
# import logging


# logger = logging.getLogger()
# logger.setLevel(logging.INFO)

# file_handler = logging.FileHandler('Run Logs')
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

def load_data(ticker: str="TQQQ"):
    file_name = "datasets/" + ticker + "_data.csv"
    try:
        data = pd.read_csv(file_name, parse_dates=True, index_col="Datetime")
        print(f"\nSuccessful load of {ticker} from CSV. \n")
    except:
        data_1 = yf.download(ticker, start="2024-09-03", end="2024-09-09", interval="1m")
        data_2 = yf.download(ticker, start="2024-09-09", end="2024-09-15", interval="1m")
        data_3 = yf.download(ticker, start="2024-09-15", end="2024-09-21", interval="1m")
        data_4 = yf.download(ticker, start="2024-09-21", end="2024-09-27", interval="1m")
        data_5 = yf.download(ticker, start="2024-09-27", end="2024-10-02", interval="1m")
        data = pd.concat([data_1, data_2, data_3, data_4, data_5])
        data.to_csv(file_name)
        print(f"\nSuccessful load of {ticker} from YF. \n")
    return data


def get_one_month_data(ticker, interval, month, api_key):
    try:
        api_key = os.environ["api_key"]
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval={interval}&apikey={api_key}&month={month}&outputsize=full&extended_hours=false"
        r = requests.get(url)
        # print(f"\nStatus code: {r.status_code}\n")
        data = r.json()
        pd_data = pd.DataFrame(data["Time Series (1min)"])
        return pd_data
    except:
        return None


def load_data_v2(ticker: str="TQQQ", interval: str="1min"):
    filename = f"datasets/{ticker}_data.csv"
    dfs = []
    api_key = os.environ["api_key"]
    cursor = datetime.date(year=2015, month=1, day=1)
    while not cursor == datetime.date(year=2020, month=10, day=1):
        if cursor.month < 10:
            mo = f"0{cursor.month}"
        else:
            mo = f"{cursor.month}"
        month = f"{cursor.year}-{mo}"
        # cursor = cursor + datetime.timedelta(month=1)
        if cursor.month == 12:
            cursor = datetime.date(year=cursor.year+1, month=1, day=1)
        else:
            cursor = datetime.date(year=cursor.year, month=cursor.month+1, day=1)
        data = get_one_month_data(ticker, interval, month, api_key)
        if data.empty:
            break
        dfs.append(data)
        # print("data acquired")
        time.sleep(60/75)
    df = pd.concat(dfs)
    df.to_csv(filename)
    return df
        

    


class Vol(backtesting.Strategy):
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
        self.buy_or_sell_stock()

    
    def buy_or_sell_stock(self) -> None:
        if self.current_time in BUY_TIMES and self.data.Close[-1] < self.data.Close[-2]:
            self.buy_price = self.current_price
            # print(f"Buy Triggered {self.data.index[-1]}")
            self.buy()
        elif self.position.size > 0 and self.current_price < (1 - LOSS_AVERSION_PERCENT) * self.buy_price:
            # Mitigates loss
            # print(f"Sell Triggered to mitigate loss at {self.data.index[-1]}")
            self.sell()
        elif self.position.size > 0 and  self.current_price >= (1 + PROFIT_CAPTURE_PERCENT) * self.buy_price:
            # Captures some profit
            # print(f"Sell Triggered to capture profit at {self.data.index[-1]}")
            self.sell()
        elif self.position.size > 0 and  self.current_time in SELL_TIMES: #== datetime.time(hour=15, minute=55, second=0):
            # print(f"Sell Triggered {self.data.index[-1]}")
            self.sell()


class Vol_Short(backtesting.Strategy):
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




def execute_backtest(data, strat, ticker: str="TQQQ"):
    bt = backtesting.Backtest(data=data, strategy=strat, exclusive_orders=True, cash=10000)
    stats = bt.run()
    results_file_name = "results/" + ticker + f"{strat.__name__}_results.csv"
    trades_file_name = "trades/" + ticker + f"{strat.__name__}_trades.csv"
    stats.to_csv(results_file_name)
    stats["_trades"].to_csv(trades_file_name)
    print("\Test finished.\n")
    graph_file_name = "graphs/" + ticker + f"{strat.__name__}_Vol.html"
    # bt.plot(filename=graph_file_name)

def execute_backtest_v2(data, strat, start, end, ticker: str="TQQQ", money=10000):
    bt = backtesting.Backtest(data=data, strategy=strat, exclusive_orders=True, cash=money)
    stats = bt.run()
    return stats["Equity Final [$]"]

def col_rename(c):
    if c == None or c == "unnamed":
        return "Datetime"
    return c.split()[1].capitalize()


if __name__=="__main__":
    # tickers = ["TQQQ"]#, "GOOG", "MSFT", "META", "NVDA", "TBIO"]
    # strats = [Vol]#, Vol_Short]
    # for ticker in tickers:
    #     for strat in strats:
    #         data = load_data_v2(ticker=ticker)
    #         execute_backtest(data=data, strat=strat, ticker=ticker)
    # api_key = os.environ["api_key"]
    # cursor = datetime.date(year=2015, month=1, day=1)
    # # money = 10000
    # # moneys=[]
    # while not cursor == datetime.date(year=2024, month=1, day=1):
    #     if cursor.month < 10:
    #         mo = f"0{cursor.month}"
    #     else:
    #         mo = f"{cursor.month}"
    #     month = f"{cursor.year}-{mo}"
    #     # cursor = cursor + datetime.timedelta(month=1)
    #     if cursor.month == 12:
    #         cursor = datetime.date(year=cursor.year+1, month=1, day=1)
    #     else:
    #         cursor = datetime.date(year=cursor.year, month=cursor.month+1, day=1)
    #     data = get_one_month_data("TQQQ", "1min", month, api_key).transpose()\
    #                                                              .rename(col_rename, axis='columns')
    #     data.index.name = "Datetime"
    #     data.to_csv('datasets/TQQQ_data.csv', mode="a")
        # data.index.astype(str)
        # data = data.astype({"Open": float, "High": float, "Low": float, "Close": float, "Volume": int})
        # print(data.index[-1])
        # exit()
        # if data.empty:
        #     break
        # money = execute_backtest_v2(data=data, strat=Vol, start=datetime.date(year=2015, month=1, day=1), end=datetime.date(year=2020, month=1, day=1), money=money)
        # moneys.append(money)
    # df = pd.DataFrame(moneys)
    # df.to_csv('res.csv')
    # peak = df.max
    # trough = df.min
    # max_drawdown = (peak - trough)/peak
    # ret = (moneys[-1] - 10000)/10000
    # sharpe = (ret - 1.16)/df.std()
    # print(f"Return: {ret}\nMax Drawdown: {max_drawdown}\nSharpe Ratio: {sharpe}")
    data = load_data()
    # print(data)
    data = data.astype({"Open": float, "High": float, "Low": float, "Close": float, "Volume": int})
    execute_backtest(data, strat=Vol)