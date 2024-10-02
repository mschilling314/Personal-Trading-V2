import logging
import datetime.datetime as dt


logging.basicConfig(filename="logs/main_log.log", format="%(asctime)s %(message)s" filemode="a")

logger = logging.getLogger()


logger.info(f"Time is now {dt.now()}")
