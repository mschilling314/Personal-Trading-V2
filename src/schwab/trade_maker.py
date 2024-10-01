import requests
import json
from src.constants.constants import TRADES_URL
from src.schwab.authenticator import get_access_token


def place_order(acct_number, quantity, instruction: str, ticker: str="TQQQ", order_type: str="MARKET"):
    """
    Places an order for an equity.  TODO: update to wait for a second then confirm trade went thru

    Inputs:
    ------
    acct_number: the Schwab account number to be passed.  DO NOT STORE IN PLAINTEXT!!!!
    quantity: The number of stocks to buy.
    instruction:  must be "BUY" or "SELL".
    ticker:  The ticker to use with Schwab
    order_type: what kind of order to place (usually just MARKET)
    """
    if instruction not in ["BUY", "SELL"]:
        raise Exception("Invalid instruction!")
    url = f"{TRADES_URL}/accounts/{acct_number}/orders"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {get_access_token()}'
    }
    order = {"orderType": order_type,
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


def _trade_successful_huh() -> bool:
    # TODO:  check to make sure the previous trade was successful
    pass