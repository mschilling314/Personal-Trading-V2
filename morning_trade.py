"""
In the morning, we want to potentially buy stocks, and place the OCO order if we do.  BUT, we also want to check to make sure the orders go thru, and retry until they do.
"""
from os import environ

from src.schwab.auth import get_access_token
from src.schwab.account import get_account_positions
from src.schwab.order import place_market_order, place_oco_order
from src.stock_data.yfin import get_current_price
from src.logger.logger import init_logger



# init
ticker = environ["Ticker"]
logger = init_logger()
logger.info("Morning run started.")
try:
    access_token = get_access_token()
except:
    logger.critical("Error fetching access token.")
    exit()

# First, we check to see how much money we have
acct = get_account_positions(access_token=access_token)
logger.debug(f"Account state at day start:\n{acct}")
money = acct["liquidity"]
# TODO: implement logic to decide if we want to buy or not, for now assume we always do
# gets the current price, then calculates sale prices
curr_price = get_current_price()
profit_capture_price = 1.025 * curr_price
loss_stop_price = 0.99 * curr_price
loss_price = loss_stop_price - 0.01
logger.debug(f"The current price is {curr_price}.  Spread has a high of {profit_capture_price} and low of {loss_stop_price}")

# ordering time
quantity = money / curr_price
market_order_resp = place_market_order(access_token=access_token, quantity=quantity, instruction="BUY", ticker=ticker)
logger.debug(f"Bought {quantity} of {ticker}, here's the response:\n{market_order_resp}")
# TODO: make sure market order went thru
oco_order_resp = place_oco_order(access_token=access_token, quantity=quantity, limit_price=profit_capture_price, stop_limit_price=loss_stop_price, stop_price=loss_price, ticker=ticker)
logger.debug(f"Set OCO order, here's the response:\n{oco_order_resp}")
# TODO: make sure OCO order is received
logger.debug(f"Morning run complete.")

