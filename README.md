# Algorithmic Trading - Python

This repository contains a complete Python-based algorithmic trading bot with Docker containerization, database integration, and technical analysis capabilities.

## Project Structure

```
Algorithmic Trading - Python/
├── Install_miniconda.py/
│   └── miniconda.py              # Miniconda installer script
├── src/                          # Trading application modules
│   ├── __init__.py
│   ├── data_fetcher.py          # Fetch market data (yfinance)
│   ├── strategy.py              # Trading strategy implementation
│   └── database.py              # Database models and operations
├── config.py                     # Configuration management
├── main.py                       # Application entry point
├── .env                          # Secrets (DO NOT commit)
├── .env.example                  # Configuration template (commit this)
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container definition
├── docker-compose.yml            # Multi-container orchestration
├── keys/                         # RSA keys directory
├── certs/                        # SSL certificates directory
├── logs/                         # Application logs
├── data/                         # Market data storage
├── README.md                     # This file
└── Setup/Helper Scripts
    ├── docker.py
    ├── setup.py
    ├── generate_rsa_keys.py
    ├── generate_jupyter_certificate.py
    └── jupyter_lab_config.py

## Quick Start

### Prerequisites

- Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- (Optional) WSL2 + Ubuntu for improved Docker performance on Windows
- Git (for version control)

### Initial Setup

1. **Clone/Download the project:**

```bash
cd "c:\Users\aryan\OneDrive\Documents\ML Projects\Python\Algorithmic Trading - Python"
```

2. **Copy environment template:**

```bash
cp .env.example .env
# Edit .env and add your API keys, database passwords, etc.
```

3. **Generate RSA keys (for security):**

```bash
python generate_rsa_keys.py --private keys/private.pem --public keys/public.pem
```

4. **Generate SSL certificate (for Jupyter Lab):**

```bash
python generate_jupyter_certificate.py --output-dir ./certs --days 365
```

5. **Install Python dependencies (if running locally):**

```bash
pip install -r requirements.txt
```

### Miniconda

You can install Miniconda using either the dedicated script or the combined installer.

Run dedicated installer:

```bash
python Install_miniconda.py/miniconda.py
```

Or run the combined installer (installs Miniconda + Docker):

```bash
python setup.py
```

Note: On Windows you may need to run PowerShell or Command Prompt as Administrator for some installer actions.

### Docker Setup & Testing

**Start the full stack (App + PostgreSQL + Redis + Jupyter Lab):**

```bash
docker-compose up --build
```

This will:
- Build the Docker image from `Dockerfile`
- Start `trading-app` container with your Python code
- Start `postgres` database
- Start `redis` cache
- Launch Jupyter Lab on `https://localhost:8888` (with SSL)

**To verify everything is working, run these commands in separate terminals:**

#### Test 1: Check Container Status

```bash
docker ps
```

You should see 3 running containers:
- `algorithmic-trading` (your app)
- `trading-db` (PostgreSQL)
- `trading-cache` (Redis)

#### Test 2: Check Docker Logs

```bash
# View trading app logs
docker logs algorithmic-trading

# View database logs
docker logs trading-db

# View Redis logs
docker logs trading-cache

# Follow logs in real-time
docker logs -f algorithmic-trading
```

#### Test 3: Access Jupyter Lab

Open your browser and go to:
```
https://localhost:8888
```

(You'll see a browser warning about self-signed certificate - that's normal. Click "Advanced" and proceed.)

#### Test 4: Test Database Connection

```bash
# Access PostgreSQL inside container
docker exec -it trading-db psql -U trader -d trading_db

# List tables
\dt

# Exit
\q
```

#### Test 5: Test Redis Connection

```bash
# Access Redis inside container
docker exec -it trading-cache redis-cli

# Ping Redis
PING

# Exit
exit
```

#### Test 6: Run Python Code in Container

```bash
# Execute Python script
docker exec algorithmic-trading python -c "import pandas; print('Pandas version:', pandas.__version__)"

# Run with Python interactive shell
docker exec -it algorithmic-trading python
```

**Stop the stack:**

```bash
docker-compose down
```

**Stop and remove volumes (WARNING: Deletes database data):**

```bash
docker-compose down -v
```

**Rebuild without cache (useful if you changed Dockerfile):**

```bash
docker-compose up --build --no-cache
```

### Local Development (Without Docker)

If you prefer to run locally without Docker:

1. **Create virtual environment:**

```bash
conda create -n trading python=3.11
conda activate trading
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Run the app:**

```bash
python main.py
```

### Generate RSA Keys

Create a 4096-bit RSA key pair (unlocked private key):

```bash
python generate_rsa_keys.py --private keys/private.pem --public keys/public.pem
```

Create an encrypted private key with a passphrase:

```bash
python generate_rsa_keys.py --private keys/private_encrypted.pem --public keys/public.pem --passphrase S3curePass
```

Verify the keys with OpenSSL:

```bash
openssl rsa -in keys/private.pem -text -noout            # private key (will ask for passphrase if encrypted)
openssl pkey -pubin -in keys/public.pem -text -noout      # public key
```

### Generate Jupyter Lab SSL Certificate

Generate a self-signed certificate for secure HTTPS access to Jupyter Lab:

```bash
python generate_jupyter_certificate.py --output-dir ./certs --days 365
```

This creates:
- `certs/jupyter.pem` — self-signed certificate
- `certs/jupyter.key` — private key

The certificate is valid for 365 days and includes Subject Alternative Names for `localhost`, `127.0.0.1`, and `jupyter-lab`.

**Access Jupyter Lab securely:**

When you run `docker-compose up --build`, Jupyter Lab will automatically start with SSL enabled on `https://localhost:8888`.

Since it's self-signed, your browser will warn you. Click "Advanced" and proceed (safe for local/dev use).

To access Jupyter Lab logs:

```bash
docker logs algorithmic-trading
```

## Module Overview

### `src/data_fetcher.py`
Fetches market data from Yahoo Finance using `yfinance`.

**Classes:**
- `DataFetcher` — Download historical and current market data

**Example usage:**
```python
from src.data_fetcher import DataFetcher

fetcher = DataFetcher(["AAPL", "MSFT"])
data = fetcher.fetch_historical_data("AAPL")
print(data.head())
```

### `src/strategy.py`
Implements trading strategies with backtesting capabilities.

**Classes:**
- `TradingStrategy` — Base strategy with SMA crossover signals

**Features:**
- Generate buy/sell signals based on moving averages
- Backtest on historical data
- Calculate returns and win rates

**Example usage:**
```python
from src.strategy import TradingStrategy

strategy = TradingStrategy(
    portfolio_size=100000,
    risk_per_trade=0.02,
    sma_short=20,
    sma_long=50
)

results = strategy.backtest(data, "AAPL")
```

### `src/database.py`
Database models for storing trades and performance metrics.

**Tables:**
- `trades` — Executed trades with entry/exit prices, P&L

**Example usage:**
```python
from src.database import Database

db = Database("postgresql://trader:password@localhost/trading_db")
db.create_tables()

# Add a trade
trade = db.add_trade("AAPL", entry_price=150.0, quantity=10)

# Close a trade
db.close_trade(trade.id, exit_price=155.0)
```

### `config.py`
Centralized configuration management.

**Reads from:**
- `.env` file (secrets, API keys)
- Environment variables
- Defaults

All settings in one place for easy management.

### `main.py`
Application entry point. Start here for the trading bot logic.

## Troubleshooting

### Docker issues

**"docker: command not found"**
- Install Docker Desktop and ensure it's added to your PATH
- Restart terminal after installation

**Container exits immediately**
- Check logs: `docker logs algorithmic-trading`
- Ensure all environment variables are set in `.env`
- Verify Python syntax in your code

**Port already in use (5432, 6379, 8888)**
- Find process using port: `netstat -ano | findstr :5432` (Windows) or `lsof -i :5432` (Mac/Linux)
- Kill process or change port in `docker-compose.yml`

### Database connection issues

**"connection refused"**
- Ensure `postgres` container is running: `docker ps`
- Check credentials in `.env` match `docker-compose.yml`
- Wait 10-15 seconds for database to initialize

**"database does not exist"**
- The database is auto-created by Docker
- If it doesn't exist, manually create: `docker exec trading-db createdb -U trader trading_db`

### Python/Import errors

**"ModuleNotFoundError: No module named 'yfinance'"**
- Reinstall dependencies: `pip install -r requirements.txt`
- Or inside Docker: `docker exec algorithmic-trading pip install yfinance`

**SSL Certificate verification failed**
- This is normal for self-signed certificates in Jupyter Lab
- Add certificate to trusted store or disable verification in dev mode

### Recommended Next Steps

1. **Implement `main.py`** — Create your trading bot logic
2. **Add more strategies** — Extend `src/strategy.py` with advanced indicators
3. **Build API endpoints** — Add Flask/FastAPI for live trading control
4. **Add monitoring** — Implement logging, metrics, alerts
5. **Deploy to cloud** — Push Docker image to AWS/GCP/DigitalOcean

---

## File Reference

| File | Purpose |
|------|---------|
| `config.py` | Configuration management (reads from `.env`) |
| `main.py` | Application entry point |
| `src/data_fetcher.py` | Fetch market data from APIs |
| `src/strategy.py` | Trading strategy implementation |
| `src/database.py` | Database models and operations |
| `Dockerfile` | Container build definition |
| `docker-compose.yml` | Multi-container orchestration |
| `requirements.txt` | Python package dependencies |
| `.env` | Secrets & API keys (local only, don't commit) |
| `.env.example` | Configuration template (commit this) |
| `.gitignore` | Git ignore rules |
| `README.md` | This documentation |

---

## Git Workflow

**Initialize repository:**
```bash
git init
git add .
git commit -m "Initial commit: Trading bot setup"
```

**What gets committed:**
```
✓ Source code (main.py, src/*, config.py)
✓ Documentation (README.md)
✓ Configuration templates (.env.example)
✓ Dependencies (requirements.txt)
✓ Containers (Dockerfile, docker-compose.yml)
```

**What is NOT committed (see `.gitignore`):**
```
✗ .env (secrets)
✗ keys/ (private RSA keys)
✗ certs/ (SSL certificates)
✗ logs/ (application logs)
✗ data/ (downloaded market data)
✗ __pycache__/ (compiled files)
```

---

## Resources

- [yfinance Documentation](https://github.com/ranaroussi/yfinance)
- [Pandas Documentation](https://pandas.pydata.org/)
- [Docker Documentation](https://docs.docker.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Book: Python for Algorithmic Trading](https://asset.quant-wiki.com/pdf/Python%20for%20Algorithmic%20Trading_%20From%20Idea%20to%20Cloud%20Deployment.pdf)
