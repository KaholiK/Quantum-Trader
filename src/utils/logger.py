# src/utils/logger.py

from loguru import logger
import sys

def setup_logger():
    logger.remove()  # Remove default logger
    logger.add(sys.stdout, level="INFO")
    logger.add("logs/quantumtrader.log", rotation="1 week", retention="4 weeks", compression="zip")
