import os
from typing import Literal
import requests
import json
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(filename="../../logs/app.log", format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)


def place_market_order(access_token, quantity, instruction: Literal["BUY", "SELL"], ticker: str="TQQQ") -> requests.Response:
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
    base_url = os.environ["Schwab_base_url"]
    acct_number = os.environ["Schwab_acct_number"]

    if instruction not in ["BUY", "SELL"]:
        logger.error(f"Was given a weird instruction: {instruction}")
        raise Exception("Invalid instruction!")
    
    url = f"{base_url}/accounts/{acct_number}/orders"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
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
    response = requests.request(method="POST", url=url, headers=headers, data=json.dumps(order))
    logger.debug(f"Here's Schwab's response to placing the market order:\n{response}")
    logger.info("Market order placed.")
    return response


def place_oco_order(access_token, quantity, limit_price: float, stop_limit_price: float, stop_price: float, ticker: str="TQQQ") -> requests.Response:
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
    base_url = os.environ["Schwab_base_url"]
    acct_number = os.environ["Schwab_acct_number"]
    url = f"{base_url}/accounts/{acct_number}/orders"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
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
    response = requests.request(method="POST", headers=headers, data=json.dumps(order))
    logger.debug(f"Schwab's response to placing the OCO order is:\n{response}")
    logger.info("OCO order placed.")
    return response


def cancel_order(access_token, order_id: str) -> requests.Response:
    """
    Cancel order, mostly for EOD or emergencies.
    """
    logger.info(f"Cancelling order {order_id}")
    base_url = os.environ["Schwab_base_url"]
    acct_number = os.environ["Schwab_acct_number"]
    url = f"{base_url}/accounts/{acct_number}/orders/{order_id}"
    headers={'Authorization': f'Bearer {access_token}'}
    response = requests.request(method="DELETE", url=url, headers=headers)
    logger.debug(f"Schwab's response to order cancellation is:\n{response}")
    logger.info(f"Order {order_id} should be cancelled.")
    return response