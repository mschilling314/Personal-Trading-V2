"""
In the afternoon, we want to see if we've sold our stock.  If we haven't, we need to sell immediately for market price and cancel the OCO orders.

We also want to add transaction data to our trading_data.sqlite database, and perhaps also yfinance data?
"""
import os
import pandas as pd
import sqlite3

from src.schwab.order import place_market_order
from src.schwab.auth import get_access_token
from src.schwab.account import get_account_positions, get_transactions_from_today
from src.logger.logger import init_logger


# intitialization
ticker = os.environ["TICKER"]
logger = init_logger()
logger.info("Morning run started.")
try:
    access_token = get_access_token()
except:
    logger.critical("Error getting access token.")
    exit()

# retrieve account positions and transactions
acct = get_account_positions(access_token=access_token)
logger.debug(f"EoD account state:\n{acct}")
money = acct["liquidity"]
positions = acct["positions"]
txns_today = get_transactions_from_today(access_token=access_token)
logger.debug(f"Today's Transactions:\n{txns_today}")

# if we have one transaction today, that means we have an open position we need to close
if len(txns_today) == 1:
    logger.warn("Position left open.\n")
    for ticker, position in positions.items():
        response = place_market_order(access_token=access_token, quantity=position["quantity"], instruction="SELL", ticker=ticker)
        logger.debug(f"Response from Schwab is:\n{response}")
        # TODO: Add a check here to make sure order goes thru?
    txns_today = get_transactions_from_today(access_token=access_token)
    logger.debug(f"Updated transactions for today:\n{txns_today}")
    # may not need, since the orders expire at EOD anyway
    # orders = get_orders_from_today(access_token=access_token)
    # for order in orders:
    #     if order["orderLegCollection"]["instruction"] == "SELL":
    #         cancel_order(access_token=access_token, order_id=order["orderId"])

# now we just need to update the database
df = pd.DataFrame(txns_today)
conn = sqlite3.connect("trading_data.sqlite")
df.to_sql("trading_data.sqlite", con=conn, if_exists="append")
logger.info("Afternoon run finished.")





