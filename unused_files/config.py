""" Application Configuration File
Centralized configuration for the trading bot
"""
import os
from pathlib   import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

#base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CERTS_DIR = BASE_DIR / "certs"
KEYS_DIR = BASE_DIR / "keys"

# Create directories if they don't exist
for directory in [CERTS_DIR, LOGS_DIR, DATA_DIR]:
    directory.mkdir(exist_ok=True)

# ================== ENVIRONMENT ==================
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT == "development"

# ================== LOGGING ==================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "trading_bot.log"

# ================== DATABASE ==================
DB_ENGINE = os.getenv("DB_ENGINE", "postgresql")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_USER = os.getenv("DB_USER", "trader")
DB_PASSWORD = os.getenv("DB_PASSWORD", "trading_password")
DB_NAME = os.getenv("DB_NAME", "trading_db")

# Database URL
DATABASE_URL = f"{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ================== REDIS CACHE ==================
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# ================== API KEYS ==================
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
BROKER_API_KEY = os.getenv("BROKER_API_KEY", "")
BROKER_API_SECRET = os.getenv("BROKER_API_SECRET", "")

# ================== MARKET DATA ==================
# Which stocks to track
STOCKS = ["AAPL", "MSFT", "GOOGL", "TSLA"]

# Data update frequency (seconds)
DATA_UPDATE_INTERVAL = int(os.getenv("DATA_UPDATE_INTERVAL", 60))

# Timeframe for analysis (minutes)
TIMEFRAME = int(os.getenv("TIMEFRAME", 5))

# ================== TRADING PARAMETERS ==================
# Risk management
PORTFOLIO_SIZE = float(os.getenv("PORTFOLIO_SIZE", 100000))  # $100k
RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", 0.02))   # 2% per trade
MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", 0.1)) # 10% per position

# Technical indicators
SMA_SHORT = int(os.getenv("SMA_SHORT", 20))   # 20-day moving average
SMA_LONG = int(os.getenv("SMA_LONG", 50))    # 50-day moving average
RSI_PERIOD = int(os.getenv("RSI_PERIOD", 14))
RSI_OVERBOUGHT = int(os.getenv("RSI_OVERBOUGHT", 70))
RSI_OVERSOLD = int(os.getenv("RSI_OVERSOLD", 30))

# ================== SSL CERTIFICATES ==================
JUPYTER_CERT = CERTS_DIR / "jupyter.pem"
JUPYTER_KEY = CERTS_DIR / "jupyter.key"

# ================== RSA KEYS ==================
RSA_PRIVATE_KEY = KEYS_DIR / "private.pem"
RSA_PUBLIC_KEY = KEYS_DIR / "public.pem"

# ================== JUPYTER LAB ==================
JUPYTER_PORT = int(os.getenv("JUPYTER_PORT", 8888))
JUPYTER_TOKEN = os.getenv("JUPYTER_TOKEN", "")

# ================== FEATURE FLAGS ==================
ENABLE_LIVE_TRADING = os.getenv("ENABLE_LIVE_TRADING", "False").lower() == "true"
ENABLE_BACKTESTING = os.getenv("ENABLE_BACKTESTING", "True").lower() == "true"
ENABLE_PAPER_TRADING = os.getenv("ENABLE_PAPER_TRADING", "True").lower() == "true"