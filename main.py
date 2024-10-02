import logging
from datetime import datetime
import yfinance as yf
import pandas as pd

logging.basicConfig(filename="logs/main_log.log", format="%(asctime)s %(message)s", filemode="a")

logger = logging.getLogger()

logger.setLevel(logging.INFO)
logger.info(f"Time is now {datetime.now()}")

yahoo = yf.download("TQQQ", period="1d", interval="1m")
df = pd.DataFrame(yahoo)
df.to_csv("trading_data.csv")