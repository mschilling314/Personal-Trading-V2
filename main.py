import logging
from datetime import datetime

logging.basicConfig(filename="logs/main_log.log", format="%(asctime)s %(message)s", filemode="a")

logger = logging.getLogger()


logger.info(f"Time is now {datetime.now()}")
