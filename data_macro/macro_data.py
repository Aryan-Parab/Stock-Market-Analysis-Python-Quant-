"""
Task 2.2 — FRED Macroeconomic Data
====================================
Downloads: Federal Funds Rate, 10Y Treasury, 2Y Treasury,
           Unemployment Rate, CPI, and computes the yield curve spread.
Merges all series onto your existing price date index using forward-fill.

Required:
    pip install requests pandas

Get a free FRED API key at: https://fred.stlouisfed.org/docs/api/api_key.html
"""

import os
import time
import logging
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────

FRED_API_KEY = os.getenv("FRED_API_KEY", "your_key_here")
FRED_BASE    = "https://api.stlouisfed.org/fred/series/observations"
DATA_DIR     = Path("data/macro")

# Series to download: {column_name: FRED_series_id}
FRED_SERIES = {
    "fed_funds_rate": "FEDFUNDS",     # Overnight rate – monthly
    "treasury_10y":   "DGS10",        # 10-year Treasury yield – daily
    "treasury_2y":    "DGS2",         # 2-year Treasury yield – daily
    "unemployment":   "UNRATE",       # Unemployment rate – monthly
    "cpi":            "CPIAUCSL",     # Consumer Price Index – monthly
}

# ── Fetch helpers ─────────────────────────────────────────────────────────────

def fetch_fred_series(
    series_id: str,
    start_date: str = "2000-01-01",
    end_date: str   = None,
    retries: int    = 3,
) -> pd.Series:
    """
    Download one FRED series and return a DatetimeIndex pd.Series.
    Handles rate limits with exponential back-off.
    """
    if end_date is None:
        end_date = datetime.today().strftime("%Y-%m-%d")

    params = {
        "series_id":         series_id,
        "api_key":           FRED_API_KEY,
        "file_type":         "json",
        "observation_start": start_date,
        "observation_end":   end_date,
    }

    for attempt in range(retries):
        try:
            resp = requests.get(FRED_BASE, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            if "observations" not in data:
                raise ValueError(f"Unexpected FRED response for {series_id}: {data}")

            records = [
                (obs["date"], obs["value"])
                for obs in data["observations"]
                if obs["value"] != "."          # FRED uses "." for missing values
            ]

            if not records:
                log.warning("No observations returned for %s", series_id)
                return pd.Series(dtype=float, name=series_id)

            dates, values = zip(*records)
            series = pd.Series(
                data  = pd.to_numeric(values, errors="coerce"),
                index = pd.to_datetime(dates),
                name  = series_id,
                dtype = float,
            )
            log.info("  ✓ %s  →  %d observations  (%s → %s)",
                     series_id, len(series), series.index[0].date(), series.index[-1].date())
            return series

        except requests.exceptions.HTTPError as e:
            if resp.status_code == 429:
                wait = 2 ** attempt * 5
                log.warning("Rate limited on %s — waiting %ds", series_id, wait)
                time.sleep(wait)
            else:
                raise
        except requests.exceptions.RequestException as e:
            log.error("Request failed for %s (attempt %d): %s", series_id, attempt + 1, e)
            if attempt == retries - 1:
                raise

    return pd.Series(dtype=float, name=series_id)


# ── Derived indicators ────────────────────────────────────────────────────────

def compute_yield_spread(df_macro: pd.DataFrame) -> pd.DataFrame:
    """10Y minus 2Y yield curve spread. Negative = inverted = recession warning."""
    if "treasury_10y" in df_macro.columns and "treasury_2y" in df_macro.columns:
        df_macro["yield_spread_10y2y"] = (
            df_macro["treasury_10y"] - df_macro["treasury_2y"]
        )
        log.info("  ✓ yield_spread_10y2y computed")
    else:
        log.warning("Cannot compute yield spread — missing 10Y or 2Y data")
    return df_macro


def compute_cpi_yoy(df_macro: pd.DataFrame) -> pd.DataFrame:
    """Year-over-year CPI change — the inflation rate the Fed actually targets."""
    if "cpi" in df_macro.columns:
        df_macro["cpi_yoy"] = df_macro["cpi"].pct_change(12) * 100
        log.info("  ✓ cpi_yoy (year-over-year %%) computed")
    return df_macro


# ── Alignment ────────────────────────────────────────────────────────────────

def align_macro_to_prices(
    price_index: pd.DatetimeIndex,
    df_macro: pd.DataFrame,
) -> pd.DataFrame:
    """
    Reindex macro data (monthly / weekly) onto a daily price date index.

    Strategy:
        1. Combine both indexes so no price date is dropped.
        2. Sort chronologically.
        3. Forward-fill macro values — last known reading carries forward
           (e.g. June UNRATE applies to all June trading days).
        4. Keep only the price dates, dropping any macro-only dates.

    This is the correct economic interpretation: we only know the
    unemployment rate *after* the BLS releases it, so we carry the
    last reported value forward until the next release.
    """
    combined_index = price_index.union(df_macro.index).sort_values()

    aligned = (
        df_macro
        .reindex(combined_index)           # introduces NaN on price-only dates
        .ffill()                           # carry last known value forward
        .reindex(price_index)              # drop macro-only dates
    )

    missing_pct = aligned.isnull().mean() * 100
    for col, pct in missing_pct.items():
        if pct > 5:
            log.warning("Column '%s' is %.1f%% missing after alignment", col, pct)

    log.info("Macro aligned: %d rows × %d columns", len(aligned), len(aligned.columns))
    return aligned


# ── Main download function ────────────────────────────────────────────────────

def download_macro_data(
    start_date:  str = "2000-01-01",
    end_date:    str = None,
    cache:       bool = True,
) -> pd.DataFrame:
    """
    Download all FRED series and return a single merged DataFrame.
    Caches raw series to CSV to avoid redundant API calls.

    Returns
    -------
    pd.DataFrame
        Columns: fed_funds_rate, treasury_10y, treasury_2y, unemployment,
                 cpi, yield_spread_10y2y, cpi_yoy
        Index:   DatetimeIndex (daily, gaps where market was closed)
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    series_frames = {}

    for col_name, series_id in FRED_SERIES.items():
        cache_path = DATA_DIR / f"{series_id}.csv"

        if cache and cache_path.exists():
            log.info("Loading cached %s from %s", series_id, cache_path)
            s = pd.read_csv(cache_path, index_col=0, parse_dates=True).squeeze()
            s.name = series_id
        else:
            log.info("Fetching %s from FRED...", series_id)
            s = fetch_fred_series(series_id, start_date=start_date, end_date=end_date)
            if not s.empty:
                s.to_csv(cache_path, header=True)

        series_frames[col_name] = s
        time.sleep(0.3)   # polite rate-limiting between requests

    # Merge all series on a shared daily index
    df_macro = pd.DataFrame(series_frames)
    df_macro.index.name = "date"
    df_macro = df_macro.sort_index()

    # Derived columns
    df_macro = compute_yield_spread(df_macro)
    df_macro = compute_cpi_yoy(df_macro)

    log.info("Raw macro dataframe: %d rows × %d columns", *df_macro.shape)
    return df_macro


# ── Merge with price data ─────────────────────────────────────────────────────

def merge_with_prices(
    df_prices:  pd.DataFrame,
    df_macro:   pd.DataFrame,
) -> pd.DataFrame:
    """
    Align macro data to the price dataframe's date index and left-join.

    Parameters
    ----------
    df_prices : DataFrame with DatetimeIndex (daily OHLCV)
    df_macro  : DataFrame returned by download_macro_data()

    Returns
    -------
    DataFrame with price columns + macro columns, same row count as df_prices.
    """
    aligned_macro = align_macro_to_prices(df_prices.index, df_macro)
    df_combined   = df_prices.join(aligned_macro, how="left")

    log.info(
        "Combined dataframe: %d rows × %d columns  (%s → %s)",
        len(df_combined),
        len(df_combined.columns),
        df_combined.index[0].date(),
        df_combined.index[-1].date(),
    )
    return df_combined


# ── Macro regime labels (bonus) ───────────────────────────────────────────────

def add_regime_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Append simple binary regime columns.
    These become powerful categorical features in ML models
    and help understand strategy performance attribution.

    Regimes:
        rate_hiking      — Fed Funds rising (3M rolling trend > 0)
        yield_inverted   — 10Y-2Y spread < 0 (classic recession signal)
        high_inflation   — CPI YoY above 3%
        high_unemployment — UNRATE above 6%
    """
    if "fed_funds_rate" in df.columns:
        rate_3m_change = df["fed_funds_rate"].diff(3)
        df["regime_rate_hiking"] = (rate_3m_change > 0).astype(int)

    if "yield_spread_10y2y" in df.columns:
        df["regime_yield_inverted"] = (df["yield_spread_10y2y"] < 0).astype(int)

    if "cpi_yoy" in df.columns:
        df["regime_high_inflation"] = (df["cpi_yoy"] > 3.0).astype(int)

    if "unemployment" in df.columns:
        df["regime_high_unemployment"] = (df["unemployment"] > 6.0).astype(int)

    regime_cols = [c for c in df.columns if c.startswith("regime_")]
    log.info("Regime labels added: %s", regime_cols)
    return df


# ── CLI / demo ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if FRED_API_KEY == "your_key_here":
        print(
            "\n⚠️  Set your FRED API key:\n"
            "   export FRED_API_KEY='your_actual_key_here'\n"
            "   Get one free at https://fred.stlouisfed.org/docs/api/api_key.html\n"
        )
        sys.exit(1)

    print("\n── Step 1: Download macro series from FRED ──")
    df_macro = download_macro_data(start_date="2010-01-01", cache=True)

    print("\n── Step 2: Simulate merging with price data ──")
    # In real use, replace this with your actual price DataFrame
    # e.g. df_prices = pd.read_csv("data/prices/SPY.csv", index_col=0, parse_dates=True)
    date_rng  = pd.bdate_range("2010-01-01", "2024-12-31")   # business days only
    df_prices = pd.DataFrame(
        index   = date_rng,
        columns = ["open", "high", "low", "close", "volume"],
        data    = 1.0,                                         # placeholder values
    )
    df_prices.index.name = "date"

    df_combined = merge_with_prices(df_prices, df_macro)

    print("\n── Step 3: Add macro regime labels ──")
    df_combined = add_regime_labels(df_combined)

    print("\n── Result ──")
    print(df_combined.tail(10).to_string())
    print(f"\nFull shape: {df_combined.shape}")
    print(f"Columns:    {list(df_combined.columns)}")

    out = DATA_DIR / "macro_combined.csv"
    df_combined.to_csv(out)
    print(f"\nSaved → {out}")
