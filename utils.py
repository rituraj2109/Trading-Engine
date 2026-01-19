import logging
import sqlite3
import pandas as pd
from config import Config
from datetime import datetime
import os

# Setup Logging
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("ForexEngine")

logger = setup_logging()

from pymongo import MongoClient

# Database Setup
def init_db():
    # SQLite Init (Legacy/Local)
    conn = sqlite3.connect(Config.DB_FILE)
    cursor = conn.cursor()
    
    # Table for News
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id TEXT PRIMARY KEY,
            date TEXT,
            title TEXT,
            source TEXT,
            sentiment_score REAL,
            currency TEXT
        )
    ''')
    
    # Table for Signals
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signals (
            time TEXT,
            pair TEXT,
            signal TEXT,
            confidence REAL,
            entry_price REAL,
            stop_loss REAL,
            take_profit REAL,
            reason TEXT
        )
    ''')
    
    # Table for Market Data & Indicators (History)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_data (
            time TEXT,
            pair TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            rsi REAL,
            macd REAL,
            atr REAL,
            ema_20 REAL,
            ema_50 REAL,
            PRIMARY KEY (time, pair)
        )
    ''')
    
    # Table for Chart Pattern History
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pattern_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            pair TEXT,
            pattern_name TEXT,
            bias TEXT,
            score REAL,
            confidence REAL
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Sqlite Database initialized.")

    # MongoDB Init Check
    if Config.MONGO_URI:
        try:
            client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
            client.server_info() # Trigger connection check
            logger.info("[OK] MongoDB Connection Successful.")
        except Exception as e:
            logger.error(f"[ERROR] MongoDB Connection Failed: {e}")

def get_db_connection():
    return sqlite3.connect(Config.DB_FILE)

def get_mongo_db():
    if not Config.MONGO_URI:
        return None
    try:
        client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=2000)
        return client.get_database("forex_engine")
    except Exception as e:
        logger.error(f"MongoDB Error: {e}")
        return None

def check_api_keys():
    """Validates that API keys are set in the environment"""
    missing_keys = []
    if Config.API_KEY_TWELVEDATA == "DEMO_KEY": missing_keys.append("TwelveData")
    if Config.API_KEY_POLYGON == "DEMO_KEY": missing_keys.append("Polygon")
    if Config.API_KEY_ALPHAVANTAGE == "DEMO_KEY": missing_keys.append("AlphaVantage")
    if Config.API_KEY_FMP == "DEMO_KEY": missing_keys.append("FMP")
    
    if missing_keys:
        logger.warning("[WARNING] MISSING API KEYS DETECTED!")
        logger.warning(f"The following services are using 'DEMO_KEY' and will be skipped: {', '.join(missing_keys)}")
        logger.warning("Ensure you have added your API keys to the Environment Variables (or .env file locally).")
    else:
        logger.info("[OK] All API keys appear to be configured.")

def is_trading_hours():
    """Check if current time is within London/NY sessions (UTC)"""
    current_hour = datetime.utcnow().hour
    return Config.TRADING_START_HOUR_UTC <= current_hour < Config.TRADING_END_HOUR_UTC

def get_utc_to_ist(dt=None):
    """Convert UTC datetime to IST"""
    from datetime import timedelta
    if dt is None:
        dt = datetime.utcnow()
    return dt + timedelta(hours=5, minutes=30)

def get_symbol_trading_hours(symbol):
    """
    Returns trading hours info for a symbol.
    Returns: dict with 'is_open', 'session_name', 'next_open_ist'
    """
    from datetime import timedelta
    
    current_utc = datetime.utcnow()
    current_hour_utc = current_utc.hour
    current_ist = get_utc_to_ist(current_utc)
    
    # Forex major pairs - 24/5 (Mon-Fri)
    forex_pairs = ["EURUSD", "GBPUSD", "USDJPY", "USDCAD", "AUDUSD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"]
    
    # Gold/Silver - Near 24/5
    commodities = ["XAUUSD", "XAGUSD"]
    
    # Crypto - 24/7
    crypto = ["BTCUSD", "ETHUSD"]
    
    # Check if weekend (Saturday=5, Sunday=6)
    weekday = current_utc.weekday()
    is_weekend = weekday >= 5
    
    # CRYPTO: Always open
    if any(c in symbol for c in crypto):
        return {
            'is_open': True,
            'session_name': 'Crypto Market (24/7)',
            'next_open_ist': None
        }
    
    # FOREX & COMMODITIES: Closed on weekends
    if is_weekend:
        # Calculate next Monday 00:00 UTC (05:30 IST)
        days_until_monday = (7 - weekday) if weekday == 6 else 1
        next_open_utc = current_utc + timedelta(days=days_until_monday)
        next_open_utc = next_open_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        next_open_ist = get_utc_to_ist(next_open_utc)
        
        return {
            'is_open': False,
            'session_name': 'Weekend - Market Closed',
            'next_open_ist': next_open_ist.strftime('%A, %B %d at %H:%M IST')
        }
    
    # FOREX/COMMODITIES: Check active sessions
    # Major forex sessions:
    # Tokyo: 00:00-09:00 UTC (05:30-14:30 IST)
    # London: 08:00-17:00 UTC (13:30-22:30 IST) 
    # New York: 13:00-22:00 UTC (18:30-03:30 IST next day)
    
    # Peak trading hours: London + NY overlap (13:00-17:00 UTC = 18:30-22:30 IST)
    # Extended: 08:00-22:00 UTC (13:30 IST - 03:30 IST next day)
    
    session_start_utc = 8  # 13:30 IST
    session_end_utc = 22   # 03:30 IST next day
    
    is_open = session_start_utc <= current_hour_utc < session_end_utc
    
    if is_open:
        # Determine which session
        if 8 <= current_hour_utc < 13:
            session_name = 'London Session'
        elif 13 <= current_hour_utc < 17:
            session_name = 'London + NY Overlap (Peak)'
        elif 17 <= current_hour_utc < 22:
            session_name = 'New York Session'
        else:
            session_name = 'Active Trading'
            
        return {
            'is_open': True,
            'session_name': session_name,
            'next_open_ist': None
        }
    else:
        # Market closed, calculate next opening
        if current_hour_utc < 8:
            # Opens today at 8:00 UTC (13:30 IST)
            next_open_utc = current_utc.replace(hour=8, minute=0, second=0, microsecond=0)
        else:
            # Opens tomorrow at 8:00 UTC (13:30 IST)
            next_open_utc = (current_utc + timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
        
        next_open_ist = get_utc_to_ist(next_open_utc)
        
        return {
            'is_open': False,
            'session_name': 'Market Closed',
            'next_open_ist': next_open_ist.strftime('%A, %B %d at %H:%M IST')
        }
