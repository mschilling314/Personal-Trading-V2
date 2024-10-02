import yfinance as yf
import datetime


def get_current_price(ticker: str="TQQQ") -> float:
    """
    Gets the current price of a given ETF.
    """
    return yf.Ticker(ticker=ticker).info["currentPrice"]


def get_daily_stock_data(ticker: str="TQQQ"):
    pass


def get_yesterday_close(ticker: str="TQQQ") -> float:
    """
    Gets the price the market last traded at.
    """
    today = datetime.datetime.now()
    yesterday_start = (today - datetime.timedelta(days=1)).replace(hour=9, minute=30, second=0)
    yesterday_end = (today - datetime.timedelta(days=1)).replace(hour=5, minute=0, second=0)
    closing_prices = yf.download(tickers=ticker, start=yesterday_start, end=yesterday_end, interval="30m")["Close"]
    while len(closing_prices) == 0:
        yesterday_start = yesterday_start - datetime.timedelta(days=1)
        yesterday_end = yesterday_end - datetime.timedelta(days=1)
        closing_prices = yf.download(tickers=ticker, start=yesterday_start, end=yesterday_end, interval="30m")["Close"]
    return closing_prices[-1]