import time
import requests
import yfinance as yf
import pandas as pd
import datetime
import os
import yfinance as yf
import pandas as pd


def _col_rename(c):
    if c == None or c == "unnamed":
        return "Datetime"
    return c.split()[1].capitalize()


def load_data_from_yfinance(ticker: str="TQQQ"):
    """
    Basic loader, takes in a ticker and returns the last month of minute-by-minute data.
    TODO: Alter, want month split to be dynamic.
    """
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


def get_one_month_data_from_alpha_vantage(ticker: str, interval: str, month: str):
    """
    Gets one month of data from AlphaVantage's API.
    """
    try:
        api_key = os.environ["ALPHA_VANTAGE_API_KEY"]
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval={interval}&apikey={api_key}&month={month}&outputsize=full&extended_hours=false"
        response = requests.get(url)
        data = response.json()
        pd_data = pd.DataFrame(data["Time Series (1min)"])
        return pd_data
    except:
        return None


def load_data_from_alpha_vantage(ticker: str="TQQQ", interval: str="1min", start_date: datetime.date=datetime.date(2015, 1, 1), end_date: datetime.date=datetime.date(2020,1,1)):
    """
    Load data from AlphaVantage.  Useful for longer-running dense data.
    TODO: Fix data, right now appending will cause the DF to write column names over and over
    """
    filename = f"datasets/{ticker}_data.csv"
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
        data = get_one_month_data_from_alpha_vantage(ticker=ticker, interval=interval, month=month)
        if data.empty:
            # Indicates the API failed for some reason, but want to fail gracefully (i.e. not lose a ton of data being written)
            break
        data = data.transpose().rename(_col_rename, axis='columns')
        data.index.name = "Datetime"
        dfs.append(data)
        # Sleep to not be rate limited (75 requests per minute allowed)
        time.sleep(60/75)
    df = pd.concat(dfs).sort_index(ascending=False)
    df.to_csv(filename)
    return df


if __name__=="__main__":
    load_data_from_alpha_vantage(start_date=datetime.date(2024, 1, 1), end_date=datetime.date(2024,4,1))