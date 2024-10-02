import logging


def init_logger() -> logging.Logger:
    """
    Initializes a logger for use that will write to logs/app.log.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel("Debug")
    handler = logging.FileHandler("logs/app.log")
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger