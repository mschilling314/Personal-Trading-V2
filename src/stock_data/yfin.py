import yfinance as yf


def get_current_price(ticker: str="TQQQ") -> float:
    """
    Gets the current price of a given ETF.
    """
    return yf.Ticker(ticker=ticker).info["currentPrice"]


def get_daily_stock_data(ticker: str="TQQQ"):
    pass