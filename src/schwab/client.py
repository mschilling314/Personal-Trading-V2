"""
An exploration of OOP for Schwab API/trading.
"""
import base64
import datetime
import json
import logging
from typing import Literal
import pytz
import requests
import os

logger = logging.getLogger(__name__)
logging.basicConfig(filename="logs/app.log", format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)

class SchwabClient:
    """
    Client class that stores all pertinent state information and allows the execution of trades and the access of online accounts in a Pythonic manner.
    """
    def __init__(self) -> None:
        self.app_key = os.environ["SCHWAB_APP_KEY"]
        self.app_secret = os.environ["SCHWAB_APP_SECRET"]
        self.refresh_token = os.environ["SCHWAB_REFRESH_TOKEN"]
        self.base_url = os.environ["SCHWAB_BASE_URL"]
        self.acct_number = os.environ["SCHWAB_ACCT_NUMBER"]
        self.access_token = self.get_access_token()


    def get_access_token(self) -> str:
        """
        Use the refresh token stored in GitHub Secrets to retrieve a new access token which is then returned.

        TODO: Confirm return value. 
        """
        logger.debug("Entered the get_access_token function.")
        headers = {'Authorization': f'Basic {base64.b64encode(bytes(f"{self.app_key}:{self.app_secret}", "utf-8")).decode("utf-8")}',
                'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'grant_type': 'refresh_token', 'refresh_token': self.refresh_token}
        resp = requests.post('https://api.schwabapi.com/v1/oauth/token', headers=headers, data=data)
        resp.raise_for_status()

        access_token = resp["access_token"]
        logger.debug("About to return from the get_access_token function.")
        return access_token


    def place_market_order(self, quantity, instruction: Literal["BUY", "SELL"], ticker: str="TQQQ") -> requests.Response:
        """
        Places a market order for an equity.

        Inputs:
        ------
        acct_number: the Schwab account number to be passed.  DO NOT STORE IN PLAINTEXT!!!!
        quantity: The number of stocks to buy.
        instruction:  must be "BUY" or "SELL".
        ticker:  The ticker to use with Schwab
        order_type: what kind of order to place (usually just MARKET)
        """
        logger.info(f"Placing market order to {instruction} for {quantity} of {ticker}.")

        if instruction not in ["BUY", "SELL"]:
            logger.error(f"Was given a weird instruction: {instruction}")
            raise Exception("Invalid instruction!")
        
        url = f"{self.base_url}/accounts/{self.acct_number}/orders"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        order = {"orderType": "MARKET",
            "session": "NORMAL",
            "duration": "DAY",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                    "instruction": instruction,
                    "quantity": quantity,
                    "instrument": {
                        "symbol": ticker,
                        "assetType": "EQUITY"
                    }
                }
                ]
            }
        logger.debug(f"Here's the order placed: {order}")
        response = requests.post(url=url, headers=headers, data=json.dumps(order))
        logger.debug(f"Here's Schwab's response to placing the market order:\n{response}")
        logger.info("Market order placed.")
        return response


    def place_oco_order(self, quantity, limit_price: float, stop_limit_price: float, stop_price: float, ticker: str="TQQQ") -> requests.Response:
        """
        Places an OCO order, which is the strategy's underpinning, to sell in the event of loss or profit.

        Inputs
        ------
        access_token: gotten from another function
        quantity: how much ETF to sell
        limit_price: the price to sell for (to profit)
        stop_limit_price: the price that triggers loss aversion sale
        stop_price: the price to sell the stock for in the event of loss
        ticker: What could this be? :)
        """
        logger.info(f"Placing OCO order to sell {quantity} of {ticker} if price reaches a high of ${limit_price} or a loss of ${stop_limit_price}.")
        url = f"{self.base_url}/accounts/{self.acct_number}/orders"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        order = { 
            "orderStrategyType": "OCO", 
            "childOrderStrategies": [ 
            { 
                "orderType": "LIMIT", 
                "session": "NORMAL", 
                "price": limit_price, 
                "duration": "DAY", 
                "orderStrategyType": "SINGLE", 
                "orderLegCollection": [ 
                { 
                "instruction": "SELL", 
                "quantity": quantity, 
                "instrument": { 
                "symbol": ticker, 
                "assetType": "EQUITY" 
                } 
                } 
                ] 
            }, 
            { 
                "orderType": "STOP_LIMIT", 
                "session": "NORMAL", 
                "price": stop_price, 
                "stopPrice": stop_limit_price, 
                "duration": "DAY", 
                "orderStrategyType": "SINGLE", 
                "orderLegCollection": [ 
                { 
                "instruction": "SELL", 
                "quantity": 2, 
                "instrument": { 
                "symbol": "XYZ", 
                "assetType": "EQUITY" 
                } 
                } 
                ] 
            } 
            ] 
            }
        logger.debug(f"The order placed looks like this:\n{order}")
        response = requests.post(url=url, headers=headers, data=json.dumps(order))
        logger.debug(f"Schwab's response to placing the OCO order is:\n{response}")
        logger.info("OCO order placed.")
        return response


    def cancel_order(self, order_id: str) -> requests.Response:
        """
        Cancel order, mostly for EOD or emergencies.
        """
        logger.info(f"Cancelling order {order_id}")
        url = f"{self.base_url}/accounts/{self.acct_number}/orders/{order_id}"
        headers={'Authorization': f'Bearer {self.access_token}'}
        response = requests.delete(url=url, headers=headers)
        logger.debug(f"Schwab's response to order cancellation is:\n{response}")
        logger.info(f"Order {order_id} should be cancelled.")
        return response
    

def get_transactions_from_today(self) -> requests.Response:
    """
    For the low low price of an access_token, gives you back the transactions from that day.

    TODO: refactor this to return an orders object of some sort instead
    """
    url = f"{self.base_url}/accounts/{self.acct_number}/transactions"
    today_end = datetime.datetime.now(tz=pytz.timezone("US/Eastern"))
    today_start = datetime.datetime.now(tz=pytz.timezone("US/Eastern")).replace(hour=9, minute=29, second=0)
    logging.debug(f"Getting transactions starting at {today_start} until {today_end}.")
    header = {'Authorization': f'Bearer {self.access_token}'}
    params = {
        "startDate": today_start.isoformat(),
        "endDate": today_end.isoformat(),
        "type": "TRADE"
    }
    response = requests.get(url=url, headers=header, params=params)
    logger.info(f"Schwab response to the request to get today's transactions:\n{response}")
    return response



def get_orders_from_today(self) -> requests.Response:
    """
    For the low low price of an access_token, gives you back the transactions from that day.

    TODO: refactor this to return an orders object of some sort instead
    """
    url = f"{self.base_url}/accounts/{self.acct_number}/orders"
    today_end = datetime.datetime.now(tz=pytz.timezone("US/Eastern"))
    today_start = datetime.datetime.now(tz=pytz.timezone("US/Eastern")).replace(hour=9, minute=29, second=0)
    logger.debug(f"Getting orders placed starting at {today_start} and ending at {today_end}")
    header = {'Authorization': f'Bearer {self.access_token}'}
    params = {
        "fromEnteredTime": today_start.isoformat(),
        "toEnteredTime": today_end.isoformat()
    }
    response = requests.get(url=url, headers=header, params=params)
    logger.debug(f"Schwab's response to the request to get today's orders:\n{response}")
    return response


def get_account_positions(self) -> dict:
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
    url = f"{self.base_url}/accounts/{self.acct_number}"
    header = {'Authorization': f'Bearer {self.access_token}'}
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