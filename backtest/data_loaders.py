import io
import time
import requests
import yfinance as yf
import pandas as pd
import datetime
import os


def _col_rename(c):
    if c == None or c == "unnamed":
        return "Datetime"
    return c.split()[1].capitalize()


def _find_prior_monday(date_of_interest: datetime.date) -> datetime.date:
    cursor = date_of_interest
    while not cursor.weekday() == 0:
        cursor -= datetime.timedelta(days=1)
    return cursor


def _get_one_week_yfinance(ticker: str, interval: str, start_date: datetime.date, end_date: datetime.date) -> pd.DataFrame:
    data = yf.download(tickers=ticker, start=start_date, end=end_date, interval=interval)
    return pd.DataFrame(data)


def load_data_from_yfinance(ticker: str="TQQQ", interval: str="1m", start_date: datetime.date=datetime.date(2024, 1, 1), end_date=datetime.date(2024, 12, 1)) -> pd.DataFrame:
    """
    Basic loader, takes in a ticker and returns the last month of minute-by-minute data.
    """
    file_name = "backtest/datasets/" + ticker + "_data.csv"
    try:
        # TODO: More complex flow wanted here, date to check and see if the data is up to date.  If not, update.  or, delete?
        data = pd.read_csv(file_name, parse_dates=True, index_col="Datetime")
        print(f"\nSuccessful load of {ticker} from CSV. \n")
    except:
        datas = []
        cursor_start = _find_prior_monday(end_date)
        datas.append(_get_one_week_yfinance(ticker, interval=interval, start_date=cursor_start, end_date=end_date))
        cursor_start -= datetime.timedelta(days=7)
        while cursor_start >= start_date and end_date - cursor_start < datetime.timedelta(days=30):
            # Fix to deal with intervals longer than a day
            datas.append(_get_one_week_yfinance(ticker, interval, cursor_start, cursor_start + datetime.timedelta(6)))
            cursor_start -= datetime.timedelta(days=7)
        data = pd.concat(datas)
        data.to_csv(file_name)
        print(f"\nSuccessful load of {ticker} from YF. \n")
    return data.sort_index(ascending=False)


def load_day_data_yfinance(ticker: str="BTC-USD", start_date: datetime.date=datetime.date(2016, 1, 1), end_date: datetime.date=datetime.date(2024, 12, 1)) -> pd.DataFrame:
    btc_ticker = yf.Ticker(ticker=ticker)
    data = pd.DataFrame(btc_ticker.history(start=start_date, end=end_date, interval="1d"))
    data = data.sort_index(ascending=True)
    file_name = "backtest/datasets/" + ticker + "_data.csv"
    data.to_csv(file_name)
    # print(f"Successful load of {ticker} from YFinance for daily data between {start} and {end}.\n")
    return data



def _get_one_month_data_from_alpha_vantage(data_function: str, api_key: str, ticker: str, interval: str, month: str) -> pd.DataFrame:
    """
    Gets one month of data from AlphaVantage's API.
    """
    try:
        url = "https://www.alphavantage.co/query"
        params = {"function": data_function, "symbol": ticker, "interval": interval, "apikey": api_key, "month": month, "outputsize": "full", "extended_hours": "false"}
        response = requests.get(url, params=params)
        data = response.json()
        key_to_access = f"Time Series ({interval})"
        pd_data = pd.DataFrame(data[key_to_access])
        return pd_data
    except Exception as e:
        print(data)
        return pd.DataFrame()


def load_stock_data_from_alpha_vantage(data_function: str="TIME_SERIES_INTRADAY", ticker: str="TQQQ", interval: str="1min", start_date: datetime.date=datetime.date(2015, 1, 1), end_date: datetime.date=datetime.date(2020,1,1)) -> pd.DataFrame:
    """
    Load data from AlphaVantage.  Useful for longer-running dense data.
    TODO:  fix so data_function works with non-default arguments
    
    Inputs:
    ticker: from NASDAQ
    interval: MUST BE IN 1min, 5min, 15min, 30min, 60min
    start_date: when to start the data
    end_date: when to end the data
    """
    api_key = os.environ["ALPHA_VANTAGE_API_KEY"]
    if interval not in ["1min", "5min", "15min", "30min", "60min"]:
        raise ValueError()
    filename = f"backtest/datasets/{ticker}_data.csv"
    dfs = []
    cursor = start_date
    while not cursor == end_date:
        if cursor.month < 10:
            mo = f"0{cursor.month}"
        else:
            mo = f"{cursor.month}"
        month = f"{cursor.year}-{mo}"
        if cursor.month == 12:
            cursor = datetime.date(year=cursor.year+1, month=1, day=1)
        else:
            cursor = datetime.date(year=cursor.year, month=cursor.month+1, day=1)
        data = _get_one_month_data_from_alpha_vantage(data_function=data_function, api_key=api_key, ticker=ticker, interval=interval, month=month)
        if data.empty:
            print(data)
            raise Exception(f"AlphaVantage API has failed.  Last call used {month}")
        data = data.transpose().rename(_col_rename, axis='columns')
        data.index.name = "Datetime"
        dfs.append(data)
        # Sleep to not be rate limited (75 requests per minute allowed)
        time.sleep(60/75)
    df = pd.concat(dfs).sort_index(ascending=False)
    df.to_csv(filename)
    return df


def get_daily_crypto_data(data_function: str="DIGITAL_CURRENCY_DAILY", symbol: str="BTC", market: str="USD") -> pd.DataFrame:
    api_key = os.environ["ALPHA_VANTAGE_API_KEY"]
    filename = f"backtest/datasets/{symbol}_data.csv"

    url = "https://www.alphavantage.co/query"
    params = {"function": data_function, "symbol": symbol, "market": market, "apikey": api_key, "datatype": "csv"}
    response = requests.get(url, params=params)
    
    df = pd.read_csv(io.StringIO(response.text), index_col="timestamp").sort_index(ascending=False)
    df.columns = df.columns.str.capitalize()
    df.to_csv(filename)
    return df



if __name__=="__main__":
    # load_stock_data_from_alpha_vantage(data_function = "TIME_SERIES_DAILY", start_date=datetime.date(2024, 1, 1), end_date=datetime.date(2024,4,1))
    load_day_data_yfinance(start="2020-01-01")
    