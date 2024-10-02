"""
Idea here is that this should deal with all things account-based.  This includes getting the account order history (ongoing and historic), positions (money and ETF), etc.
"""
import os
import requests
import datetime
import pytz
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(filename="/logs/app.log", format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)


def get_transactions_from_today(access_token) -> requests.Response:
    """
    For the low low price of an access_token, gives you back the transactions from that day.
    """
    base_url = os.environ["Schwab_base_url"]
    acct_number = os.environ["Schwab_acct_number"]
    url = f"{base_url}/accounts/{acct_number}/transactions"
    today_end = datetime.datetime.now(tz=pytz.timezone("US/Eastern"))
    today_start = datetime.datetime.now(tz=pytz.timezone("US/Eastern")).replace(hour=9, minute=29, second=0)
    logging.debug(f"Getting transactions starting at {today_start} until {today_end}.")
    header = {'Authorization': f'Bearer {access_token}'}
    params = {
        "startDate": today_start.isoformat(),
        "endDate": today_end.isoformat(),
        "type": "TRADE"
    }
    response = requests.get(url=url, headers=header, params=params)
    logger.info(f"Schwab response to the request to get today's transactions:\n{response}")
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
    logger.debug(f"Getting orders placed starting at {today_start} and ending at {today_end}")
    header = {'Authorization': f'Bearer {access_token}'}
    params = {
        "fromEnteredTime": today_start.isoformat(),
        "toEnteredTime": today_end.isoformat()
    }
    response = requests.get(url=url, headers=header, params=params)
    logger.debug(f"Schwab's response to the request to get today's orders:\n{response}")
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
    logger.debug(f"Schwab's response to the request for account positions:\n{response}")
    # TODO: Check to make sure response is valid
    liquidity = response["securitiesAccount"]["currentBalances"]["buyingPowerNonMarginableTrade"]
    logger.debug(f"Stored liquidity: {liquidity}")
    positions = response["securitiesAccount"]["positions"]
    logger.debug(f"Positions object type: {type(positions)}")
    positions_dict = {}
    for position in positions:
        ticker = position["instrument"]["symbol"]
        quantity = position["longQuantity"]
        price = position["marketValue"]
        positions_dict[ticker] = {"quantity": quantity, "price": price}
        logger.debug(f"Stored position with key {ticker} and value {positions_dict[ticker]}.")
    ret_obj = {"liquidity": liquidity, "positions": positions_dict}
    logger.debug(f"Will return:\n{ret_obj}")
    return ret_obj