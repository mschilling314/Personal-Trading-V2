import os
import requests
import json


def place_market_order(access_token, quantity, instruction: str, ticker: str="TQQQ") -> requests.Response:
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
    base_url = os.environ["Schwab_base_url"]
    acct_number = os.environ["Schwab_acct_number"]

    if instruction not in ["BUY", "SELL"]:
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
    response = requests.request(method="POST", url=url, headers=headers, data=json.dumps(order))
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
    response = requests.request(method="POST", headers=headers, data=json.dumps(order))
    return response


def cancel_order(access_token, order_id: str) -> requests.Response:
    """
    Cancel order, mostly for EOD or emergencies.
    """
    base_url = os.environ["Schwab_base_url"]
    acct_number = os.environ["Schwab_acct_number"]
    url = f"{base_url}/accounts/{acct_number}/orders/{order_id}"
    headers={'Authorization': f'Bearer {access_token}'}
    response = requests.request(method="DELETE", url=url, headers=headers)
    return response