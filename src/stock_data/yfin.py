from yfinance import Ticker, download
from os import getcwd
from os.path import join
from datetime.datetime import now
from datetime import timedelta
import logging


logger = logging.getLogger(__name__)
log_file_path = join(getcwd(), "logs", "app.log")
logging.basicConfig(filename=log_file_path, format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)


def get_current_price(ticker: str="TQQQ") -> float:
    """
    Gets the current price of a given ETF.
    """
    logger.debug(f"Getting current price of {ticker}.")
    return Ticker(ticker=ticker).info["currentPrice"]


def get_daily_stock_data(ticker: str="TQQQ"):
    pass


def get_yesterday_close(ticker: str="TQQQ") -> float:
    """
    Gets the price the market last traded at.
    """
    logger.debug(f"Trying to get previous closing price of {ticker}.")
    today = now()
    yesterday_start = (today - timedelta(days=1)).replace(hour=9, minute=30, second=0)
    yesterday_end = (today - timedelta(days=1)).replace(hour=5, minute=0, second=0)
    logger.debug(f"Trying to get the close prices from {yesterday_start} to {yesterday_end}.")
    closing_prices = download(tickers=ticker, start=yesterday_start, end=yesterday_end, interval="30m")["Close"]
    while len(closing_prices) == 0:
        logger.debug(f"Market must've been closed on {yesterday_end}")
        yesterday_start = yesterday_start - timedelta(days=1)
        yesterday_end = yesterday_end - timedelta(days=1)
        logger.debug(f"Trying again for {yesterday_start} to {yesterday_end}.")
        closing_prices = download(tickers=ticker, start=yesterday_start, end=yesterday_end, interval="30m")["Close"]
    logger.debug(f"Closing prices are:\n{closing_prices}")
    return closing_prices[-1]