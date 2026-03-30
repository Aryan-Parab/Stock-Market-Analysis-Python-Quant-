# fred macroeconomic data
import os
import time
import logging
from turtle import pd
import requests
from pathlib import Path
from datetime import datetime, timedelta

logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt = '%H:%M:%S')
log = logging.getLogger(__name__)

# Configuration
FRED_API_KEY = os.getenv('FRED_API_KEY', "your_fred_api_key_here") # READS THE KEY FROM THE ENVIRONMENT NOT FROM THE CODE
FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations" # URL THAT ALL THE FRED DATA COMES FROM
DATA_DIR = Path('data_macro') # ALL THE DATA WILL BE STORED IN THIS FOLDER
DATA_DIR.mkdir(exist_ok=True)

# Series to download {column_name: fred_series_id}}
FRED_SERIES = {
    "fed_funds_rate": "FEDFUNDS", # overnight rate-monthly
    "treasury_10yr": "DGS10", # 10 year treasury yield-daily
    "treasure_2yr": "DGS2", # 2 year treasury yield-daily
    "unemployment": "UNRATE", # unemployment rate-monthly
    "cpi": "CPIAUCSL", # consumer price index-monthly

}

# fetch helpers
def fetch_fred_data(series_id, start_date, end_date, retries:int = 3)-> pd.Series:
    if end_date is None:
        end_date = datetime.today().strftime('%Y-%m-%d')

    params = {
        "series_id":series_id,  
        "api_key": FRED_API_KEY,
        "file_type":"json",
        "observation_start": start_date,
    }
    for attempt in range(retries):
        try:
            response = requests.get(FRED_BASE_URL, params = params, timeout = 15)
            response.raise_for_status()
            data = response.json()
            if "observations":
                pass
        except:
            pass