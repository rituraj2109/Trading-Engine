import sqlite3
import requests
import pandas as pd
import hashlib
import time as time_module
from datetime import datetime, timedelta
from config import Config
from utils import logger, get_db_connection

class DataLoader:
    def __init__(self):
        self.session = requests.Session()
        self.last_api_call = {}  # Track last API call time for rate limiting
        # Cache symbols that TwelveData reports as unavailable on current plan
        self.td_unavailable = set()

    def _rate_limit(self, api_name, min_delay=1.0):
        """Enforce minimum delay between API calls"""
        if api_name in self.last_api_call:
            elapsed = time_module.time() - self.last_api_call[api_name]
            if elapsed < min_delay:
                time_module.sleep(min_delay - elapsed)
        self.last_api_call[api_name] = time_module.time()
    
    def _generate_news_id(self, title, date):
        """Create a unique ID for news deduplication"""
        return hashlib.md5(f"{title}{date}".encode()).hexdigest()

    def save_news_to_db(self, news_items):
        """
        news_items: List of dicts {date, title, source, text, currency}
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Mongo Connection
        db_mongo = None
        if Config.MONGO_URI:
            from utils import get_mongo_db
            db_mongo = get_mongo_db()

        count = 0
        for item in news_items:
            # Simple keyword matching for currency if not provided
            currency = item.get('currency', 'USD') # Default to USD relevance
            
            news_id = self._generate_news_id(item['title'], item['date'])
            
            try:
                # SQL Save
                cursor.execute('''
                    INSERT INTO news (id, date, title, source, sentiment_score, currency)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (news_id, item['date'], item['title'], item['source'], 0.0, currency))
                
                # Mongo Save (Upsert)
                if db_mongo is not None:
                     db_mongo.news.update_one(
                        {"id": news_id},
                        {"$set": {
                            "id": news_id,
                            "date": item['date'],
                            "title": item['title'],
                            "source": item['source'],
                            "text": item['text'],
                            "sentiment_score": 0.0,
                            "currency": currency
                        }},
                        upsert=True
                     )

                count += 1
            except sqlite3.IntegrityError:
                continue # Duplicate
        
        conn.commit()
        conn.close()
        if count > 0:
            logger.info(f"Saved {count} new news items.")

    def fetch_news_fmp(self):
        """Fetch news from Financial Modeling Prep"""
        if Config.API_KEY_FMP == "DEMO_KEY": 
            return []
            
        url = f"{Config.URL_FMP}/fmp/articles?page=0&size=50&apikey={Config.API_KEY_FMP}"
        try:
            resp = self.session.get(url)
            if resp.status_code == 200:
                data = resp.json()
                news = []
                for article in data.get('content', []):
                    # Filter for Forex if possible or general economic news
                    news.append({
                        'date': article['date'],
                        'title': article['title'],
                        'source': 'FMP',
                        'text': article['content'], # Strip html in real app
                        'currency': 'USD' # FMP is mostly US market data
                    })
                return news
        except Exception as e:
            logger.error(f"FMP News Fetch Error: {e}")
        return []

    def fetch_news_newsapi(self):
        """Fetch general forex/economy news from NewsAPI or NewsData.io"""
        if Config.API_KEY_NEWSAPI == "DEMO_KEY":
            return []
            
        # Check if using NewsData.io (Key starts with 'pub_')
        if Config.API_KEY_NEWSAPI.startswith("pub_"):
            # NewsData.io implementation
            url = f"{Config.URL_NEWSDATA}/news?apikey={Config.API_KEY_NEWSAPI}&q=forex OR inflation&language=en"
            try:
                resp = self.session.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    articles = data.get('results', [])
                    news = []
                    for art in articles:
                        news.append({
                            'date': art.get('pubDate', datetime.utcnow().isoformat()),
                            'title': art.get('title'),
                            'source': 'NewsData.io',
                            'text': art.get('description') or "",
                            'currency': 'USD'
                        })
                    return news
                else:
                    logger.error(f"NewsData.io Error: {resp.text}")
            except Exception as e:
                logger.error(f"NewsData.io Fetch Error: {e}")
            return []
            
        # Default NewsAPI.org implementation
        # Searching for keywords like 'forex', 'central bank', 'inflation'
        url = f"{Config.URL_NEWSAPI}/everything?q=forex OR inflation OR 'central bank'&sortBy=publishedAt&apiKey={Config.API_KEY_NEWSAPI}"
        try:
            resp = self.session.get(url)
            if resp.status_code == 200:
                articles = resp.json().get('articles', [])
                news = []
                for art in articles:
                    news.append({
                        'date': art['publishedAt'],
                        'title': art['title'],
                        'source': 'NewsAPI',
                        'text': art['description'] or "",
                        'currency': 'USD' # Broad assumption
                    })
                return news
            else:
                logger.error(f"NewsAPI.org Error: {resp.text}")
        except Exception as e:
            logger.error(f"NewsAPI Fetch Error: {e}")
        return []

    def fetch_news_finnhub(self):
        """Fetch general news from Finnhub"""
        if Config.API_KEY_FINNHUB == "DEMO_KEY":
            return []
            
        url = f"{Config.URL_FINNHUB}/news?category=forex&token={Config.API_KEY_FINNHUB}"
        try:
            resp = self.session.get(url)
            if resp.status_code == 200:
                data = resp.json()
                news = []
                for article in data:
                    news.append({
                        'date': datetime.fromtimestamp(article.get('datetime', 0)).isoformat(),
                        'title': article.get('headline'),
                        'source': 'Finnhub',
                        'text': article.get('summary') or "",
                        'currency': 'USD' # Broad assumption
                    })
                return news
            else:
                logger.error(f"Finnhub Error: {resp.text}")
        except Exception as e:
            logger.error(f"Finnhub Fetch Error: {e}")
        return []

    def fetch_price_polygon(self, symbol, interval="15", outputsize=100):
        """Fetch forex candles from Polygon.io"""
        if Config.API_KEY_POLYGON == "DEMO_KEY":
            return None
        
        # Rate limiting: Polygon free tier has 5 calls/minute limit
        self._rate_limit('polygon', min_delay=12.0)
        
        # Polygon Symbol format: C:EURUSD (e.g. C:XAUUSD)
        ticker = f"C:{symbol}"
        end = datetime.now().strftime('%Y-%m-%d')
        start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Requests handles params better
        url = f"{Config.URL_POLYGON}/v2/aggs/ticker/{ticker}/range/{interval}/minute/{start}/{end}"
        params = {
            "adjusted": "true",
            "sort": "asc",
            "limit": outputsize,
            "apiKey": Config.API_KEY_POLYGON
        }
        
        try:
            resp = self.session.get(url, params=params)
            
            # Handle rate limit (429) specifically
            if resp.status_code == 429:
                logger.warning(f"Polygon rate limit hit for {symbol}. Skipping.")
                return None
                
            data = resp.json()
            
            # Check for error response
            if data.get('status') == 'ERROR':
                error_msg = data.get('error', data.get('message', 'Unknown error'))
                if 'rate limit' in error_msg.lower() or 'exceeded' in error_msg.lower():
                    logger.warning(f"Polygon rate limit for {symbol}. Use TwelveData instead.")
                else:
                    logger.error(f"Polygon API error for {symbol}: {error_msg}")
                return None
            
            # Accept OK or DELAYED. data['results'] must exist.
            if data.get('resultsCount', 0) > 0 and 'results' in data:
                df = pd.DataFrame(data['results'])
                df['datetime'] = pd.to_datetime(df['t'], unit='ms')
                df = df.rename(columns={'o':'open', 'h':'high', 'l':'low', 'c':'close'})
                df = df[['datetime', 'open', 'high', 'low', 'close']]
                df = df.sort_values('datetime')
                return df
            else:
                 # Log detailed status if failed
                 logger.warning(f"Polygon no data for {symbol}: Status={data.get('status')}, Count={data.get('resultsCount')}")
        except Exception as e:
            logger.error(f"Polygon Exception for {symbol}: {e}")
        return None

    def fetch_price_twelvedata(self, symbol, interval="15min", outputsize=100):
        """Fetch forex candles from Twelve Data"""
        if Config.API_KEY_TWELVEDATA == "DEMO_KEY":
            return None

        # If we've previously seen this symbol flagged as unavailable on TwelveData plan, skip immediately
        if symbol.upper() in self.td_unavailable:
            logger.info(f"Skipping TwelveData for {symbol} — previously marked unavailable on current plan.")
            return None

        # Rate limiting: Wait at least 1 second between calls (free tier: 8 calls/min)
        self._rate_limit('twelvedata', min_delay=1.0)

        # TwelveData prefers "EUR/USD" format
        # Ensure Uppercase
        symbol = symbol.upper()
        td_symbol = symbol
        if len(symbol) == 6 and '/' not in symbol:
             td_symbol = f"{symbol[:3]}/{symbol[3:]}"
             
        # Use params to handle encoding of "/"
        url = f"{Config.URL_TWELVEDATA}/time_series"
        params = {
            "symbol": td_symbol,
            "interval": interval,
            "outputsize": outputsize,
            "apikey": Config.API_KEY_TWELVEDATA
        }
        
        try:
            resp = self.session.get(url, params=params)
            data = resp.json()
            if 'values' in data:
                df = pd.DataFrame(data['values'])
                df['datetime'] = pd.to_datetime(df['datetime'])
                df['open'] = df['open'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['close'] = df['close'].astype(float)
                df['volume'] = 0 
                df = df.sort_values('datetime')
                return df
            else:
                msg = data.get('message') or str(data)
                logger.error(f"TwelveData error for {symbol} ({td_symbol}): {msg}")
                # Detect plan/availability related messages and cache the symbol to avoid repeated failing calls
                lowered = (msg or "").lower()
                if 'grow' in lowered or 'available starting' in lowered or 'plan' in lowered or 'not available' in lowered:
                    try:
                        self.td_unavailable.add(symbol.upper())
                        logger.info(f"Marked {symbol} as unavailable on TwelveData for this plan — will skip next time.")
                    except Exception:
                        pass
        except Exception as e:
            logger.error(f"TwelveData Exception: {e}")
        return None

    def fetch_price_alphavantage(self, symbol, interval="15min"):
        """Backup: Fetch forex candles from Alpha Vantage"""
        if Config.API_KEY_ALPHAVANTAGE == "DEMO_KEY":
            return None
        
        # Rate limiting: AlphaVantage free tier has 5 calls/minute, 500 calls/day
        self._rate_limit('alphavantage', min_delay=12.0)
        
        # AV uses from/to currency format, e.g., EUR to USD
        # Assuming symbol is like EURUSD, we split it.
        # Note: accurate splitting often requires a mapping if pairs aren't standard 3+3 (e.g. commodities)
        from_currency = symbol[:3]
        to_currency = symbol[3:]
        
        url = f"{Config.URL_ALPHAVANTAGE}?function=FX_INTRADAY&from_symbol={from_currency}&to_symbol={to_currency}&interval={interval}&apikey={Config.API_KEY_ALPHAVANTAGE}"
        try:
            resp = self.session.get(url)
            data = resp.json()
            key_name = f"Time Series FX ({interval})"
            if key_name in data:
                df = pd.DataFrame(data[key_name]).T
                df = df.rename(columns={
                    '1. open': 'open',
                    '2. high': 'high',
                    '3. low': 'low',
                    '4. close': 'close'
                })
                df.index = pd.to_datetime(df.index)
                df['datetime'] = df.index
                df = df.sort_values('datetime')
                df['open'] = df['open'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['close'] = df['close'].astype(float)
                return df
            else:
                logger.error(f"AlphaVantage error for {symbol}: {data.get('Note') or data.get('Error Message')}")
        except Exception as e:
            logger.error(f"AlphaVantage Exception: {e}")
        return None

    def fetch_indicator_taapi(self, symbol, indicator="rsi", interval="15m"):
        """Fetch specific indicator from Taapi.io"""
        if Config.API_KEY_TAAPI == "DEMO_KEY":
            logger.warning(f"Taapi API Key is missing (using DEMO_KEY). Skipping {symbol}.")
            return None
        
        # Taapi requires specific symbol formats, often exchange specific.
        # For Forex, generic usage might be tricky without paying.
        # Trying generic request.
        url = f"{Config.URL_TAAPI}/{indicator}?secret={Config.API_KEY_TAAPI}&symbol={symbol}&interval={interval}"
        try:
             resp = self.session.get(url)
             if resp.status_code == 200:
                 return resp.json().get('value')
             else:
                 logger.error(f"Taapi Error: {resp.text}")
        except Exception as e:
            logger.error(f"Taapi Exception: {e}")
        return None

    def fetch_market_data(self, symbol):
        """Try TwelveData first (most reliable), then Polygon, fall back to AlphaVantage"""
        # TwelveData is prioritized as it's working reliably
        df = self.fetch_price_twelvedata(symbol)
        
        if df is None or df.empty:
            logger.info(f"TwelveData failed/skipped for {symbol}, trying Polygon...")
            df = self.fetch_price_polygon(symbol)
            
        if df is None or df.empty:
            logger.warning(f"Polygon failed for {symbol}, trying AlphaVantage...")
            df = self.fetch_price_alphavantage(symbol)
        return df

    def fetch_all_news(self):
        """Aggregates news from all sources"""
        all_news = []
        n1 = self.fetch_news_fmp()
        n2 = self.fetch_news_newsapi()
        n3 = self.fetch_news_finnhub()
        
        if n1: all_news.extend(n1)
        if n2: all_news.extend(n2)
        if n3: all_news.extend(n3)
        
        self.save_news_to_db(all_news)
