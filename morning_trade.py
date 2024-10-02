"""
In the morning, we want to potentially buy stocks, and place the OCO order if we do.  BUT, we also want to check to make sure the orders go thru, and retry until they do.
"""
import os

from src.schwab.auth import get_access_token
from src.schwab.account import get_account_positions
from src.schwab.order import place_market_order, place_oco_order
from src.stock_data.yfin import get_current_price


# init
access_token = get_access_token()
ticker = os.environ["Ticker"]

# First, we check to see how much money we have
money = get_account_positions(access_token=access_token)["liquidity"]
# TODO: implement logic to decide if we want to buy or not, for now assume we always do
# gets the current price, then calculates sale prices; for now, try setting limit order to be equiv to current loss_stop_price
curr_price = get_current_price()
profit_capture_price = 1.025 * curr_price
loss_stop_price = 0.99 * curr_price

# ordering time
quantity = money / curr_price
market_order_resp = place_market_order(access_token=access_token, quantity=quantity, instruction="BUY", ticker=ticker)
# TODO: make sure market order went thru
oco_order_resp = place_oco_order(access_token=access_token, quantity=quantity, limit_price=profit_capture_price, stop_limit_price=loss_stop_price, stop_price=loss_stop_price, ticker=ticker)
# TODO: make sure OCO order is received


