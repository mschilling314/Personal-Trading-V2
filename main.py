import logging
from datetime import datetime
import yfinance as yf
import pandas as pd
import sqlite3
from src.schwab.account import get_account_positions



# logging.basicConfig(filename="logs/main_log.log", format="%(asctime)s %(message)s", filemode="a")

# logger = logging.getLogger()

# logger.setLevel(logging.INFO)
# logger.info(f"Time is now {datetime.now()}")

# yahoo = yf.download("TQQQ", period="1d", interval="1m")
# df = pd.DataFrame(yahoo)
# conn = sqlite3.connect("trading_data.sqlite")
# df.to_sql(name="TQQQ", con=con, if_exists="append")