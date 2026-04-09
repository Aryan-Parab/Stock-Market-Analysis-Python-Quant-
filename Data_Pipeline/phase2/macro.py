# fred macroeconomic data
from email import errors
from dotenv import load_dotenv
import logging 
from logging.handlers import RotatingFileHandler
import os
import time
import pandas as pd  
import requests
from pathlib import Path
from datetime import datetime, timedelta


log = logging.getLogger(__name__)
DATA_DIR = Path('data_macro') # ALL THE DATA WILL BE STORED IN THIS FOLDER
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR = DATA_DIR/'logs'
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt = '%H:%M:%S')
file_handler = RotatingFileHandler(LOG_DIR /'macro.log', maxBytes = 1024 *1024, backupCount = 5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt = '%Y-%m-%d %H:%M:%S'))
logging.getLogger().addHandler(file_handler)

# Configuration
#FRED_API_KEY = "1c9faac63039de9c90a7897d6363ddfd" # READS THE KEY FROM THE ENVIRONMENT NOT FROM THE CODE
load_dotenv() # loads environment variables from .env file into the system environment
FRED_API_KEY = os.getenv("FRED_API_KEY")

if not FRED_API_KEY:
    log.error("FRED API key not found. Please check the key in your .env file.")

    raise ValueError("FRED_API_KEY environment variable is not set.")

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations" # URL THAT ALL THE FRED DATA COMES FROM
DATA_DIR = Path('data_macro') # ALL THE DATA WILL BE STORED IN THIS FOLDER
DATA_DIR.mkdir(exist_ok=True)

# Series to download {column_name: fred_series_id}} 
# left side column names , right side = fred series ids
# we are pulling interest rates, yeild curve, inflatio, and labor market
FRED_SERIES = {
    "fed_funds_rate": "FEDFUNDS", # overnight rate-monthly
    "treasury_10yr": "DGS10", # 10 year treasury yield-daily
    "treasury_2yr": "DGS2", # 2 year treasury yield-daily
    "unemployment": "UNRATE", # unemployment rate-monthly
    "cpi": "CPIAUCSL", # consumer price index-monthly

}

# fetch helpers - download one time series from fred with retries and error handling, returns list of (date, value) tuples
def fetch_fred_data(series_id, start_date, end_date, retries:int = 3): # fetch a single macroecconomic time series

# define cache file path
    cache  = DATA_DIR / F"{series_id}.csv"

# check if file already exisists
    if cache.exists():
        log.info("Loading %s from cache at %s", series_id, cache)
        series = pd.read_csv(cache, index_col = 0, parse_dates = True).squeeze()
        series.name = series_id
        return series

    if end_date is None: # if end date is not provided, use today's date as default
        end_date = datetime.today().strftime('%Y-%m-%d')

# this dict is sent to the api to specify needs
    params = {
        "series_id":series_id,  
        "api_key": FRED_API_KEY,
        "file_type":"json",
        "observation_start": start_date,
        "observation_end": end_date
    }
    for attempt in range(retries): # tries API call multiple times
        try:
            response = requests.get(FRED_BASE_URL, params = params, timeout = 15)
            # send https request to fred, include params as query string 
            response.raise_for_status() # error handling for http errors
            data = response.json() # convert data into json format
            if "observations" not in data: # prevent silent failures if API returns unexpected format
                raise ValueError (f"Unexpected FRED response for {series_id}: {data}")
            
            # loops through all the observations and extracts date, value, skip missing values
            records = [
                (obs['date'], obs['value']) 
                for obs in data['observations']
                if obs['value']!="."
                ] # filter out missing values
            
            if not records: # handle empty data
                log.warning("No observations returned for %s",series_id)
                return pd.Series(dtype = float, name = series_id)
            
            # zip records - split the list of (date, value)pairs into 2 separate lists
            # pd.to_datetime(dates) - converts string dates like "2015-01-02" into proper pandas date objects
            # pd.to_numeric(..., errors = 'coerce') converts string values like 2.12 into actual numbers, anything that 
            # cannot be converted becomes Nan

            dates, values = zip(*records) # unzip into separate lists
            series = pd.Series(data = pd.to_numeric(values, errors = 'coerce'),index = pd.to_datetime(dates),
                name = series_id,dtype = float)
            
# Save to cache for future use
            series.to_csv(cache, header = True)
            log.info("Saved %s to cache at %s", series_id, cache)
            return series
        
# error handling 
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429: # too many request, wait and try again
                wait_time = 2**attempt*5
                log.warning("Rate limit on %s, waiting %d seconds before retrying...", series_id, wait_time )
                time.sleep(wait_time)
            else:
                raise e
            
        except requests.exceptions.RequestException as e:
            log.error("Request failed for %s (attempt%d): %s", series_id, attempt +1,e)
            if attempt == retries -1:
                raise e
            
    return pd.Series(dtype = float, name = series_id)

# # Main Dowload function

def download_macro_data(start_date, end_date):
    df_macro = pd.DataFrame() # empty dataframe to store all the macro data
    for name, series_id in FRED_SERIES.items():
        log.info("Downloading %s (%s)", name, series_id)
        series = fetch_fred_data(series_id, start_date, end_date)
        df_macro[name] = series
    df_macro.sort_index(inplace = True) # sort the index by date
    return df_macro

# if __name__ == "__main__":
#       print("Downloading macro data...")
#       df = download_macro_data("2015-01-01", None)

 #----------------------- Derived Indicators -----------------------
#positive  - Normal economy health, Near Zero -> Caution - slow down possible
#Negative - Inverted recession making


def compute_yield_curve(df_macro: pd.DataFrame) -> pd.DataFrame:
    """10Y minus 2Y yield curve spread. Negative = inverted = recession warning."""
    if "treasury_10yr" in df_macro.columns and "treasury_2yr" in df_macro.columns:
        df_macro["yield_curve"] = (df_macro["treasury_10yr"] - df_macro["treasury_2yr"]) 
        # simple subtraction of two columns results in the yield curve spread
        log.info("Computed yield curve spread")
    
    else:
        log.warning("Cannot compute yield curve spread - missing data (10yr or 2yr)")

    return df_macro

def compute_cpi_yoy(df_macro: pd.DataFrame) -> pd.DataFrame:
    """Year-over-year change in CPI as a measure of inflation."""
    if "cpi" in df_macro.columns:
        df_macro["cpi_yoy"] = df_macro["cpi"].pct_change(12) * 100
        log.info("Computed CPI year-over-year change")
    else:
        log.warning("Cannot compute CPI YoY - missing CPI data")
    
    return df_macro


if __name__ == "__main__":
    df = download_macro_data("2026-04-08", None)
    df = compute_yield_curve(df)
    df = compute_cpi_yoy(df)
    print(df.head())