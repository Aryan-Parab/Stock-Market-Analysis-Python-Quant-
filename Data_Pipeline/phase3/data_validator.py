import pandas as pd
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))
from Data_Pipeline.phase1.fetch_data import DataFetcher
fetcher = DataFetcher('AAPL', '2020-01-01', '2020-12-31')
data = fetcher.fetch_data_yfinance('AAPL', '2020-01-01', '2020-12-31')

# Vaidation function
def validate(data):
        # implement validation logic 
        issues = []

        # Flatten Multiindex columns if present
        if isinstance(data.columns, pd.MultiIndex):
                data.columns = [col[0] for col in data.columns]
        # check 1 - missing values
        null_counts = data.isnull().sum()
        if null_counts.any():
                issues.append(f"Missing values found: {null_counts[null_counts > 0].index.tolist()}")
        # check 2 - gaps in date index
        if 'Date' in data.columns:
                dates = pd.to_datetime(data['Date'])
                gaps = dates.diff().dt.days
                if gaps.max() >5:
                    issues.append("Gaps in date index detected, which may indicate missing data")
        # check 3 - outliers in price data
        if (data['Close']<0).any():
                issues.append("Negative closing prices, which is not possible")
        # check 4 - price jumps
        if (data['Close'].pct_change().abs()>0.5).any():
                issues.append("Large price jumps detected, which may indicate data errors")
        # check 5 - zero volume
        if (data['Volume']==0).any():
                issues.append("Zero trading volume detected, error in data")
        # check 6 - duplicate dates
        if 'Date' in data.columns and data['Date'].duplicated().any():
                issues.append("Duplicate dates found in data, which is not valid")
        return issues

print ("Columns:", data.columns.tolist())
print("Column Types:", type(data.columns))

issues = validate(data)
print("Validation issues:", issues)