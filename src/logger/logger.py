import logging
import os


def init_logger() -> logging.Logger:
    """
    Initializes a logger for use that will write to logs/app.log.
    """
    logger = logging.getLogger(__name__)
    log_file_path = os.path.join(os.getcwd(), "logs", "app.log")
    logging.basicConfig(filename=log_file_path, format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)
    return logger