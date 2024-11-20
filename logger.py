# logger.py
import logging


def setup_logger():
    logger = logging.getLogger('app_logger')
    logger.setLevel(logging.DEBUG)

    # Create handlers
    fh = logging.FileHandler('./logs/app.log')
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Create formatter and add it to handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Add handlers to the logger
    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger
