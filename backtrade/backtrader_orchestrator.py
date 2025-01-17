import backtrader as bt
import pandas as pd
from datetime import datetime as dt
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor


from models.dogsofthedow import Dogs
from DividendPandasData import DividendPandasData

def fetch_data(ticker: str, start: str="2000-01-01", end: str="2024-01-31", interval: str="3mo") -> tuple[str, pd.DataFrame]:
    df = yf.download(ticker, start="2000-01-01", end="2024-01-31", interval="3mo")
    df.index = df.index.tz_localize("America/New_York")
    dividends = yf.Ticker(ticker).dividends.resample("3ME").sum()
    dividends.index = dividends.index.tz_convert("America/New_York")
    df["dividends"] = dividends.reindex(df.index, method="pad").fillna(0)
    return ticker, df


def load_data_concurrently(tickers, max_workers: int=1) -> dict[str, pd.DataFrame]:
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(fetch_data, tickers))
    return {ticker: df for ticker, df in results}


if __name__=="__main__":
    cerebro = bt.Cerebro()

    dow30 = pd.read_csv("dow30.csv")
    tickers = list(dow30["SYMBOL"])

    data_dict = load_data_concurrently(tickers=tickers)

    for ticker, df in data_dict.items():
        data = DividendPandasData(dataname=df)
        cerebro.adddata(data, name=ticker)

    cerebro.addstrategy(Dogs)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')

    results = cerebro.run()
    for result in results:
        print(f"Sharpe Ratio: {result.analyzers.sharpe.get_analysis()}")
    # cerebro.plot()


