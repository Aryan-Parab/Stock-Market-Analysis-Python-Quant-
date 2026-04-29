import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import seaborn as sns

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
        self.prices = prices
        self.ticker = ticker
        self.risk_free_rate = risk_free_rate
        self.start_date = start_date
        self.end_date = end_date
        self.daily_returns = prices.pct_change().dropna()
        
    def basic_metrics(self):
        mean_return = self.daily_returns.mean()
        std_dev = self.daily_returns.std()
        daily_rf = self.risk_free_rate / 252
        # mean return is daily and risk free return is annually so we need something similar to mean return 
        # so daily_risk free is equal to mean return in terms of returns
        sharpe_ratio = (mean_return - daily_rf) / std_dev
        max_drawdown = self.max_drawdown()
        volatility = std_dev * np.sqrt(252) # trading days are 252
        annualized_return = (1+mean_return)**252 -1
        return {
            'mean_return':mean_return, 'std_dev':std_dev, 'sharpe_ratio': sharpe_ratio,
            'max_drawdown':max_drawdown, 'volatility':volatility, 'annualized_return':annualized_return
        }
        
    def max_drawdown(self):
        cumulative = (1+self.daily_returns).cumprod() # converts daily returns into a equity curve starting at 1
        rolling_max = cumulative.cummax() # at every point, what was the highest value seen so far
        drawdown = (cumulative - rolling_max) / rolling_max # how far that peak we are at every point
        return drawdown.min() # worst point ever

    def correlation_matrix(self):
        return self.daily_returns.corr()
    
    def risk_metrics(self):
        variance = self.daily_returns.var()
        skewness = self.daily_returns.skew()
        kurtosis = self.daily_returns.kurtosis()
        var_95 = np.percentile(self.daily_returns, 5)
        var_99 = np.percentile(self.daily_returns,1)
        cvar_95 = self.daily_returns[self.daily_returns<var_95].mean()
        return {
            'variance':variance,'skewness':skewness,'kurtosis':kurtosis, 'var_95':var_95, 'var_99':var_99,
            'cvar_95' :cvar_95}
    
    
    def _statistical_tests(self):
        from scipy.stats import jarque_bera
        from statsmodels.tsa.stattools import adfuller 

        jb_stat, jb_pval = stats.jarque_bera(self.daily_returns)
        adf_result = stats.adfuller(self.daily_returns)
        adf_stat = adf_result[0]
        adf_pval = adf_result[1]

        # for interpretation strings
        if jb_pval < 0.05:
            jb_interpretation = "Not normal"
        else:
            jb_interpretation = "Normal"

        if adf_pval < 0.05:
            adf_interpretation = "Stationary - safe to model"
        else:
            adf_interpretation = "Non-stationary - may not be safe to model"

        # After your if statements, add:
        return {
                'jb_stat': jb_stat,
                'jb_pval': jb_pval,
                'jb_interpretation': jb_interpretation,
                'adf_stat': adf_stat,
                'adf_pval': adf_pval,
                'adf_interpretation': adf_interpretation
}

def compute_all (self):
    # this will call all the methods and returns a single report
    results = {}
    results.update(self.basic_metrics())
    results.update(self.risk_metrics())
    results.update(self.statistical_tests())
    results['max_drawdown'] = self.max_drawdown()
    return results

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


    # At the very bottom — outside the class
if __name__ == "__main__":
    import pandas as pd
    
    # Load your saved CSV from Phase 2
    df = pd.read_csv("SPY_data.csv", parse_dates=['Date'], index_col='Date')
    prices = df['Close']
    
    # Create the object
    report = SummaryReport(
        data=df,
        prices=prices,
        ticker='SPY',
        risk_free_rate=0.05,
        start_date='2015-01-01',
        end_date='2026-04-15'
    )
    
    # NOW call print_report — this is the ON button
    report.print_report()
