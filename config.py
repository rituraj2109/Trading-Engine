import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # API Keys (User must set these in .env)
    API_KEY_FMP = os.getenv("API_KEY_FMP", "DEMO_KEY")
    API_KEY_NEWSAPI = os.getenv("API_KEY_NEWSAPI", "DEMO_KEY")
    API_KEY_TWELVEDATA = os.getenv("API_KEY_TWELVEDATA", "DEMO_KEY")
    API_KEY_ALPHAVANTAGE = os.getenv("API_KEY_ALPHAVANTAGE", "DEMO_KEY")
    API_KEY_TAAPI = os.getenv("API_KEY_TAAPI", "DEMO_KEY")
    API_KEY_FINNHUB = os.getenv("API_KEY_FINNHUB", "DEMO_KEY")
    API_KEY_POLYGON = os.getenv("API_KEY_POLYGON", "DEMO_KEY")


    # Trading Settings
    PAIRS = ["EURUSD", "USDJPY", "GBPUSD", "USDCAD", "GBPJPY", "XAUUSD", "XAGUSD"]
    TIMEFRAME = "15min"  # 15 minutes
    
    # Valid symbols for trading (extend as needed)
    VALID_SYMBOLS = [
        # Forex majors
        "EURUSD", "USDJPY", "GBPUSD", "USDCAD", "AUDUSD", "NZDUSD",
        "GBPJPY", "EURJPY", "EURGBP", "USDCHF",
        # Commodities
        "XAUUSD", "XAGUSD",
        # Crypto
        "BTCUSD", "ETHUSD",
        # Stocks (examples)
        "AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"
    ]
    
    # Risk Management
    RISK_PERCENT = 0.01  # 1% Account Risk
    MIN_RISK_REWARD = 2.0
    ATR_MULTIPLIER_SL = 1.5
    
    # Scoring Thresholds
    BUY_THRESHOLD = 3
    SELL_THRESHOLD = -3
    
    # Time Filters (IST)
    # Trading Window: 13:30 IST to 03:30 IST (Crosses midnight if viewed strictly, but effectively 08:00 UTC to 22:00 UTC)
    # 13:30 IST = 08:00 UTC
    # 03:30 IST = 22:00 UTC
    TRADING_START_HOUR_UTC = 8 
    TRADING_END_HOUR_UTC = 22

    # Database: allow override via DB_FILE env var, otherwise use local sqlite file
    DB_FILE = os.getenv("DB_FILE", "forex_engine.db")
    
    # Files
    LOG_FILE = "trading_engine.log"

    # API Endpoints
    URL_FMP = "https://financialmodelingprep.com/api/v3"
    URL_TWELVEDATA = "https://api.twelvedata.com"
    URL_ALPHAVANTAGE = "https://www.alphavantage.co/query"
    URL_NEWSAPI = "https://newsapi.org/v2"
    URL_NEWSDATA = "https://newsdata.io/api/1"
    URL_TAAPI = "https://api.taapi.io"
    URL_FINNHUB = "https://finnhub.io/api/v1"
    URL_POLYGON = "https://api.polygon.io"
