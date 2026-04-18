import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf


class DataFetcher:
    def __init__(self, ticker, start_date, end_date):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date

    def fetch_data_yfinance(self):
        try:
            df = yf.download(self.ticker, start=self.start_date, end=self.end_date, auto_adjust=True)
            df.to_csv(f"{self.ticker}_data.csv", index=False)
            df.reset_index(inplace=True)
            return df
        except Exception as e:
            print(f"Error downloading {self.ticker}: {e}")
            return None


def calculate_returns(prices):
    returns = prices.pct_change().dropna()
    return returns


def calculate_squared_returns(returns):
    squared = (returns ** 2).dropna()
    return squared


def calculate_absolute_returns(returns):
    absolute = returns.abs().dropna()
    return absolute


def plot_acf_pacf(series, title, lags=40):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    plot_acf(series, lags=lags, ax=axes[0], title=f"{title} - ACF")
    plot_pacf(series, lags=lags, ax=axes[1], title=f"{title} - PACF")
    plt.tight_layout()
    return fig


# === MAIN EXECUTION ===
tickers = ['SPY', 'AAPL', 'NVDA', 'MSFT', 'GOOGL']
start_date = '2015-01-01'
end_date = '2026-04-15'

# Download data
print("Downloading data...")
for ticker in tickers:
    fetcher = DataFetcher(ticker, start_date, end_date)
    data = fetcher.fetch_data_yfinance()
    print(f"  Downloaded {ticker}: {len(data)} rows")

# Plot for each asset
for ticker in tickers:
    df = pd.read_csv(f"{ticker}_data.csv")
    df['Close'] = pd.to_numeric(df['Close'], errors = 'coerce')
    prices = df['Close']

    returns = calculate_returns(prices)
    squared_returns = calculate_squared_returns(returns)
    absolute_returns = calculate_absolute_returns(returns)

    # Plot returns
    fig = plot_acf_pacf(returns, f"{ticker} - Returns")
    fig.savefig(f"{ticker}_returns_acf.png", dpi=150)
    print(f"Saved {ticker}_returns_acf.png")

    # Plot squared returns
    fig = plot_acf_pacf(squared_returns, f"{ticker} - Squared Returns")
    fig.savefig(f"{ticker}_squared_returns_acf.png", dpi=150)
    print(f"Saved {ticker}_squared_returns_acf.png")

    # Plot absolute returns
    fig = plot_acf_pacf(absolute_returns, f"{ticker} - Absolute Returns")
    fig.savefig(f"{ticker}_absolute_returns_acf.png", dpi=150)
    print(f"Saved {ticker}_absolute_returns_acf.png")

print("\nAll plots saved!")
