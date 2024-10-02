"""
Idea here is that this should deal with all things account-based.  This includes getting the account order history (ongoing and historic), positions (money and ETF), etc.
"""
import os
import requests
import datetime
import pytz


def get_transactions_from_today(access_token) -> requests.Response:
    """
    For the low low price of an access_token, gives you back the transactions from that day.
    """
    base_url = os.environ["Schwab_base_url"]
    acct_number = os.environ["Schwab_acct_number"]
    url = f"{base_url}/accounts/{acct_number}/transactions"
    today_end = datetime.datetime.now(tz=pytz.timezone("US/Eastern"))
    today_start = datetime.datetime.now(tz=pytz.timezone("US/Eastern")).replace(hour=9, minute=29, second=0)
    header = {'Authorization': f'Bearer {access_token}'}
    params = {
        "startDate": today_start.isoformat(),
        "endDate": today_end.isoformat(),
        "type": "TRADE"
    }
    response = requests.get(url=url, headers=header, params=params)
    return response



def get_orders_from_today(access_token) -> requests.Response:
    """
    For the low low price of an access_token, gives you back the transactions from that day.
    """
    base_url = os.environ["Schwab_base_url"]
    acct_number = os.environ["Schwab_acct_number"]
    url = f"{base_url}/accounts/{acct_number}/orders"
    today_end = datetime.datetime.now(tz=pytz.timezone("US/Eastern"))
    today_start = datetime.datetime.now(tz=pytz.timezone("US/Eastern")).replace(hour=9, minute=29, second=0)
    header = {'Authorization': f'Bearer {access_token}'}
    params = {
        "fromEnteredTime": today_start.isoformat(),
        "toEnteredTime": today_end.isoformat()
    }
    response = requests.get(url=url, headers=header, params=params)
    return response


def get_account_positions(access_token) -> dict:
    """
    Given the access token, will return the amount of money you can use to buy stock, and the stocks you own.

    Return is structured as a dictionary like so:
    {
        liquidity: a float
        positions:
        |--ticker: a string
           |--quantity: hopefully a float
           |--price: a float
    }
    """
    base_url = os.environ["Schwab_base_url"]
    acct_number = os.environ["Schwab_acct_number"]
    url = f"{base_url}/accounts/{acct_number}"
    header = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url=url, headers=header, params={"fields": "positions"})
    # TODO: Check to make sure response is valid
    liquidity = response["securitiesAccount"]["currentBalances"]["buyingPowerNonMarginableTrade"]
    positions = response["securitiesAccount"]["positions"]
    positions_dict = {}
    for position in positions:
        ticker = position["instrument"]["symbol"]
        quantity = position["longQuantity"]
        price = position["marketValue"]
        positions_dict[ticker] = {"quantity": quantity, "price": price}
    return {"liquidity": liquidity, "positions": positions_dict}