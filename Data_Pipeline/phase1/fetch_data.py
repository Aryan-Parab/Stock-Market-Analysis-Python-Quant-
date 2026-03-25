from tkinter import FALSE
import colorlog
from anyio import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import requests
import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

#from unused_files.config import DATA_DIR

# setup folders
DATA_DIR = Path('data_fetcher')
LOG_DIR = Path('data_fetcher/data_logs')
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

ALPHA_key = os.getenv('ALPHA_VANTAGE_API_KEY')

def set_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = FALSE
    logger.handlers.clear()

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt= '%Y-%m-%d %H:%M:%S'
    )

    console_formatter = colorlog.ColoredFormatter(
    "%(asctime)s | %(log_color)s%(levelname)s%(reset)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        'DEBUG':    'white',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    }
)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(LOG_DIR / 'data_fetcher.log', maxBytes=1024*1024, backupCount=5)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    return logger

logger = set_logger('data_fetcher')
logger.info("logger is working")

class DataFetcher:
    def __init__(self, ticker, start_date, end_date):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date

    # fetching data from yfinance
    def fetch_data_yfinance(self,ticker, start_date, end_date):
        try:
            logger.debug(f"Download data for {ticker} from yfinance") # debug
            df = yf.download(ticker, start=start_date, end=end_date, auto_adjust = True)
            df.to_csv(f"{ticker}_data.csv", index = False)
            if df.empty:
                logger.warning(f"No data found for {ticker}, check the ticker name or date_range")
                return None
            
            df.reset_index(inplace=True)
            logger.info(f"{ticker} data fetched successfully, shape: {df.shape}, rows: {len(df)}") # info
            return df
        except ValueError as e:
            logger.error(f"Failed to download data for {ticker}: {e}") # Error
        except Exception as e:
            logger.error(f"Unexpected crash occurred while fetching data for {ticker}: {e}") # critical
            return None
    
# ususage
fetcher_aapl = DataFetcher('AAPL', '2015-01-01', '2026-03-10')
# fetcher_googl = DataFetcher('GOOGL', '2015-01-01', '2026-03-10')
# fetcher_msft = DataFetcher('MSFT', '2015-01-01', '2026-03-10')

data=fetcher_aapl.fetch_data_yfinance('AAPL', '2015-01-01', '2026-03-10')
# data=fetcher_googl.fetch_historical_data(['GOOGL'])
# data=fetcher_msft.fetch_historical_data(['MSFT'])
print(data)


