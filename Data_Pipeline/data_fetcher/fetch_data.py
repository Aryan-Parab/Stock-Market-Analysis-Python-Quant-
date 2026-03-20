import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import requests
import os


ALPHA_key = os.getenv('ALPHA_VANTAGE_API_KEY')

class DataFetcher:
    def __init__(self, ticker, start_date, end_date):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date

    # fetching data from yfinance
    def fetch_data_yfinance(self,ticker, start_date, end_date):
        df = yf.download(ticker, start=start_date, end=end_date, auto_adjust = True)
        df.reset_index(inplace=True)
        return df

    # fetch real time data
    def fetch_real_time_data(self,ticker):
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_key}"
        params = {'function': 'GLOBAL_QUOTE', 'symbol': ticker, 'apikey': ALPHA_key}
        response = requests.get(url, params=params)
        return response.json()
    
    # fetching historical data
    def fetch_historical_data(self,tickers, start= '2015-01-01', end='2026-03-10'):
        data ={}
        for i in tickers:
            try:
                df=self.fetch_data_yfinance(i, start,end)
                df.to_csv(f"{i}_data.csv", index = False)
                data[i] = df
                print(f"Data for {i} fetched and saved with shape {df.shape} and length {len(df)}")
            except Exception as e:
                print(f"Error fetching data for {i}: {e}")
        return data
    
# ususage
fetcher_aapl = DataFetcher('AAPL', '2015-01-01', '2026-03-10')
fetcher_googl = DataFetcher('GOOGL', '2015-01-01', '2026-03-10')
fetcher_msft = DataFetcher('MSFT', '2015-01-01', '2026-03-10')

data=fetcher_aapl.fetch_historical_data(['AAPL'])
data=fetcher_googl.fetch_historical_data(['GOOGL'])
data=fetcher_msft.fetch_historical_data(['MSFT'])