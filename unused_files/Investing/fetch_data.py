import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf

class Stock:
    def __init__(self, ticker, start_date, end_date):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
    
    data =[]
    for i in ticker:
        # downloading yfinance data
        df = yf.download(i, start=self.start_date, end=self.end_date)
        # print complete if data is visible or else not availble
        if df !=0:
            print(df.head())
        else:
            print("Data not available for {}".format(i))
        
        # adjusting the columns
    df.reset_index(inplace=True)

        # append 
    data.append(df)

        # convert to csv
    df.to_csv(f"{i}_data.csv", index=False)

    return df 
