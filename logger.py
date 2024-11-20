# logger.py
import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger():
    logger = logging.getLogger('app_logger')
    logger.setLevel(logging.DEBUG)

    # Define the logs directory path relative to this file
    logs_directory = os.path.join(os.path.dirname(__file__), 'logs')

    # Create the logs directory if it doesn't exist
    os.makedirs(logs_directory, exist_ok=True)

    # Create a RotatingFileHandler to prevent log files from growing indefinitely
    fh = RotatingFileHandler(os.path.join(
        logs_directory, 'app.log'), maxBytes=5*1024*1024, backupCount=5)
    fh.setLevel(logging.DEBUG)

    # Create a StreamHandler to output logs to the console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Create formatter and add it to handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Avoid adding multiple handlers if they already exist
    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger
