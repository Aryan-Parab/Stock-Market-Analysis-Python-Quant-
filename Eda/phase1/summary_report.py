import pandas as pd
import yfinance
import logging
from logging.handlers import RotatingFileHandler
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import seaborn as sns
from statsmodels.tsa.stattools import adfuller

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))
from Data_Pipeline.phase1.fetch_data import DataFetcher

# Metrics to include in the report 
'''
1. Mean daily return
2. Standard deviation of daily returns
3.  sharpe ratio, max drawdown, volatility , annuralized return,
4. Corrlation matrix of returns, p/e ratio,peg ratio, dividend yield
5. Visualizations: histogram, find outliers using box plot, time series data, scatter plot of returns, heatmap of correlation 
'''

# Risk metrics to include in the report
'''
1. Variance, and Std Deviation
2. Skewness -> negative (fat left tail) = crash risk market,
3. Kurtosis -> >3 ( fat tails) = higher probability of extreme events.
4. Var 95% -> worst loss on 95% of days
5. Var 99% -> worst loss on 99% of days
6. CVar 95% -> more accurate than Var (average loss beyond 95% of Var)
'''

# Ratio metrics to include in the report
'''
1. Sharpe Ratio = (mean return - risk free rate) / std_deviation
2. Max Drawdown = max(cummulative max - returns )/ cummulative max
3. Volatility = std_deviation of retuns 

'''

# Statistical test
'''
1. Jarque-bera test -> test if returns are normally distributed
p<0.05 means not normal which is true because markets doesn't follow normal dist.

2. ADF test -> test if series is stationary
p<0.05 means stationary 
3. anova test -> is it important to include in the test report?
'''

class SummaryReport:
    def __init__(self,data, prices, ticker, risk_free_rate, start_date, end_date):
        self.data = data
        self.prices = pd.to_numeric(prices, errors = 'coerce')
        self.ticker = ticker
        self.risk_free_rate = risk_free_rate # Annual rate eg: 0.05
        self.start_date = start_date
        self.end_date = end_date

        # Remove missing prices before calculating returns
        self.prices = self.prices.dropna()
        self.daily_returns = self.prices.pct_change().dropna()

        if len(self.daily_returns) <2:
            raise ValueError("Not enough valid price data.")

    # Basic metrics
    def basic_metrics(self):
        r = self.daily_returns

        mean_return = r.mean()
        median_return = r.median()

        std_dev = r.std()
        # Convert annual risk free rate to daily rate
        daily_rf = (1 + self.risk_free_rate) ** (1/252) - 1 #This converts the annual effective risk-free rate into an equivalent daily rate

        daily_sharpe = ((mean_return - daily_rf)/std_dev
                        if std_dev >0 else np.nan)
        
        # mean return is daily and risk free return is annually so we need something similar to mean return 
        # so daily_risk free is equal to mean return in terms of returns
        annual_sharpe = daily_sharpe * np.sqrt(252)
        
        max_drawdown = self.max_drawdown()
        volatility = std_dev * np.sqrt(252) # trading days are 252
        
        # annualized realized growth estimate from observed prices
        n_returns = len(r)
        annualized_return = ((self.prices.iloc[-1]/self.prices.iloc[0])**(252/n_returns)-1)
        return {
            'mean_return':mean_return, 'std_dev':std_dev, 'sharpe_ratio':annual_sharpe,
            'max_drawdown':max_drawdown, 'volatility':volatility, 'annualized_return':annualized_return,
            'median_return':r.median(),
        }

    # 2. MAXIMUM DRAWDOWN
    def max_drawdown(self):
        cumulative = (1+self.daily_returns).cumprod() # converts daily returns into a equity curve starting at 1
        rolling_max = cumulative.cummax() # at every point, what was the highest value seen so far
        drawdown = (cumulative / rolling_max -1) # how far that peak we are at every point
        
        return drawdown.min() # worst point ever

    def correlation_matrix(self):
        return self.daily_returns.corr()
    
        #3. RISK METRICS

    def risk_metrics(self):
        r = self.daily_returns

        var_95 = np.percentile(r,5)
        var_99 = np.percentile(r,1)
        
        variance = self.daily_returns.var()
        skewness = self.daily_returns.skew()
        kurtosis = self.daily_returns.kurtosis() # Excess kurtosis: normal = 0, >0 means fat tails
        
        cvar_95 = self.daily_returns[self.daily_returns<var_95].mean()
        return {
            'variance':variance,'skewness':skewness,'kurtosis':kurtosis, 'var_95':var_95, 'var_99':var_99,
            'cvar_95' :cvar_95}
     
    #4. STATISTICAL TESTS
    
    def _statistical_tests(self):
        r = self.daily_returns

        jb_result = stats. jarque_bera(r)
        adf_result = adfuller(r)

        jb_pval = jb_result.pvalue
        adf_pval = adf_result[1]

        return {
            "jb_stat": jb_result.statistic,
            "jb_pval": jb_pval,
            "jb_interpretation": (
                "Evidence against normality"
                if jb_pval < 0.05
                else "Insufficient evidence against normality"
            ),
            "adf_stat": adf_result[0],
            "adf_pval": adf_pval,
            "adf_interpretation": (
                "Reject unit-root null"
                if adf_pval < 0.05
                else "Fail to reject unit-root null"
            )
        }

# Combine all metrics

    def compute_all(self):

        results = {}
        results.update(self.basic_metrics())
        results.update(self.risk_metrics())
        results.update(self.statistical_tests())
        return results

# print report

    def print_report(self):
        results = self.compute_all()

        print("=" * 50)
        print(f"  STATISTICAL SUMMARY — {self.ticker}")
        print("=" * 50)
        
        print("\n📈 RETURN METRICS")
        print(f"  Mean Daily Return     : {results['mean_return']:.4%}")
        print(f"  Annualized Return     : {results['annualized_return']:.4%}")
        
        print("\n⚠️  RISK METRICS")
        print(f"  Volatility (Annual)   : {results['volatility']:.4%}")
        print(f"  Max Drawdown          : {results['max_drawdown']:.4%}")
        print(f"  Variance              : {results['variance']:.6f}")
        print(f"  Skewness              : {results['skewness']:.4f}")
        print(f"  Kurtosis              : {results['kurtosis']:.4f}")
        
        print("\n📊 RATIO METRICS")
        print(f"  Sharpe Ratio          : {results['sharpe_ratio']:.4f}")
        
        print("\n🎯 TAIL RISK")
        print(f"  VaR 95%               : {results['var_95']:.4%}")
        print(f"  VaR 99%               : {results['var_99']:.4%}")
        print(f"  CVaR 95%              : {results['cvar_95']:.4%}")
        
        print("\n🧪 STATISTICAL TESTS")
        print(f"  Jarque-Bera p-value   : {results['jb_pval']:.6f}")
        print(f"  Interpretation        : {results['jb_interpretation']}")
        print(f"  ADF p-value           : {results['adf_pval']:.6f}")
        print(f"  Interpretation        : {results['adf_interpretation']}")
        print("=" * 50)


from Data_Pipeline.phase1.fetch_data import DataFetcher

if __name__ == "__main__":
    fetcher = DataFetcher(
        "SPY", "2023-01-01", "2026-10-01"
    )

    df = fetcher.fetch_data_yfinance(
        "SPY", "2023-01-01", "2026-10-01"
    )

    if df is not None and not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")

        prices = df["Close"]

        report = SummaryReport(
            data=df,
            prices=prices,
            ticker="SPY",
            risk_free_rate=0.05,
            start_date="2023-01-01",
            end_date="2026-10-01"
        )

        report.print_report()