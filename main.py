import schedule
import time
import sys
import threading
from config import Config
from utils import init_db, logger, get_db_connection, check_api_keys
from data_loader import DataLoader
from sentiment import SentimentEngine
from strategy import DecisionEngine
from colorama import Fore, Style, init

# Initialize Colorama
init(autoreset=True)

def run_analysis_cycle(mode="background"):
    """
    Background cycle: Fetches news, updates sentiment, scans core pairs silently, logs to DB.
    """
    if mode == "background":
        logger.info(f"Background Cycle Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Update News & Sentiment (Global)
    loader = DataLoader()
    sentiment = SentimentEngine()
    
    # Fetch news every cycle (every 15 minutes)
    if mode == "background":
        logger.info("Fetching news from all sources...")
    loader.fetch_all_news()
    
    if mode == "background":
        logger.info("Updating sentiment scores for news...")
    sentiment.update_sentiment_scores()
    
    # 2. Analyze Core Pairs and Store Data (Every 15 Minutes)
    engine = DecisionEngine()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Mongo Connection
    db_mongo = None
    if Config.MONGO_URI:
        from utils import get_mongo_db
        db_mongo = get_mongo_db()

    if mode == "background":
        logger.info(f"Processing {len(Config.PAIRS)} symbols: {', '.join(Config.PAIRS)}")
    
    data_saved_count = 0
    signals_saved_count = 0
    
    for pair in Config.PAIRS:
        try:
            # Add delay to respect free API rate limits
            # TwelveData free tier: 8 calls/min, so ~8 seconds between calls
            # This ensures we don't exceed any API limits
            time.sleep(2)  # 2 seconds between pairs
                
            result = engine.analyze_pair(pair)
            
            # Save Market Data & Indicators (Every Cycle - Every 15 Minutes)
            if 'raw_data' in result:
                rd = result['raw_data']
                try:
                    # Convert timestamp to ISO string if needed
                    time_str = rd['time'].isoformat() if hasattr(rd['time'], 'isoformat') else str(rd['time'])
                    
                    # 1. SQL Save
                    cursor.execute('''
                        INSERT OR REPLACE INTO market_data (time, pair, open, high, low, close, rsi, macd, atr, ema_20, ema_50)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (time_str, pair, rd['open'], rd['high'], rd['low'], rd['close'], 
                          rd['rsi'], rd['macd'], rd['atr'], rd['ema_20'], rd['ema_50']))
                    
                    # 2. Mongo Save
                    if db_mongo is not None:
                        mongo_data = {
                            "time": time_str,
                            "pair": pair,
                            "open": rd['open'], "high": rd['high'], "low": rd['low'], "close": rd['close'],
                            "rsi": rd['rsi'], "macd": rd['macd'], "atr": rd['atr'],
                            "pos_atr": rd.get('pos_atr'), # Bollinger/Keltner helpers if exist
                            "ema_20": rd['ema_20'], "ema_50": rd['ema_50']
                        }
                        # Upsert based on time+pair
                        db_mongo.market_data.update_one(
                            {"pair": pair, "time": time_str},
                            {"$set": mongo_data},
                            upsert=True
                        )

                    conn.commit()
                    data_saved_count += 1
                    if mode == "background":
                        logger.info(f"✓ Saved market data & indicators for {pair} (Price: {result['price']})")
                except Exception as e:
                    logger.error(f"DB Save Error {pair}: {e}")

            # Log ALL signals to DB (including WAIT) for tracking
            # This allows you to see market state even when closed
            cursor.execute('''
                INSERT INTO signals (time, pair, signal, confidence, entry_price, stop_loss, take_profit, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (result['time'], pair, result['signal'], result['confidence'], 
                  result['price'], result['stop_loss'], result['take_profit'], result['reason']))
            
            # Mongo Save Signal
            if db_mongo is not None:
                signal_doc = {
                    "time": result['time'],
                    "pair": pair,
                    "signal": result['signal'],
                    "confidence": result['confidence'],
                    "entry_price": result['price'],
                    "stop_loss": result['stop_loss'],
                    "take_profit": result['take_profit'],
                    "reason": result['reason'],
                    "created_at": datetime.utcnow()
                }
                db_mongo.signals.insert_one(signal_doc)

            conn.commit()
            signals_saved_count += 1
            if mode == "background":
                logger.info(f"[SIGNAL] Saved signal for {pair}: {result['signal']} at {result['time']}")
            
            # Save Chart Patterns to History
            if 'pattern_details' in result and result['pattern_details']:
                for pattern_name, details in result['pattern_details'].items():
                    cursor.execute('''
                        INSERT INTO pattern_history (time, pair, pattern_name, bias, score, confidence)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (result['time'], pair, pattern_name, details['bias'], 
                          details['score'], details['confidence']))
                    
                    if db_mongo is not None:
                        db_mongo.pattern_history.insert_one({
                            "time": result['time'],
                            "pair": pair,
                            "pattern_name": pattern_name,
                            "bias": details['bias'],
                            "score": details['score'],
                            "confidence": details['confidence']
                        })

                conn.commit()
            
            # Only log BUY/SELL signals to console in background mode
            if mode == "background" and result['signal'] != "WAIT":
                logger.info(f"🚨 TRADING SIGNAL: {pair} {result['signal']} ({result['confidence']}%)")
                if result.get('patterns'):
                    logger.info(f"   📊 Patterns: {', '.join(result['patterns'])}")
        except Exception as e:
            logger.error(f"Error analyzing {pair}: {e}")

    conn.close()
    if mode == "background":
        logger.info(f"✓ Stored {data_saved_count} market data records with indicators")
        logger.info(f"✓ Stored {signals_saved_count} signal records")
        logger.info("Background Cycle Complete - Next cycle in 15 minutes.")

def background_job():
    """Thread target for scheduler"""
    schedule.every(15).minutes.do(run_analysis_cycle, mode="background")
    while True:
        schedule.run_pending()
        time.sleep(1)

def print_report(result):
    color = Fore.YELLOW
    if result['signal'] == "BUY": color = Fore.GREEN
    elif result['signal'] == "SELL": color = Fore.RED
    
    print(f"\n{Style.BRIGHT}----------------------------------------")
    print(f"{Style.BRIGHT}SYMBOL: {result['pair']} | SIGNAL: {color}{result['signal']}{Style.RESET_ALL}{Style.BRIGHT}")
    print(f"TIME (IST): {result.get('time_ist', result['time'])}")
    
    # Show session info
    if 'session_info' in result:
        session = result['session_info']
        if session['is_open']:
            print(f"{Fore.GREEN}SESSION: {session['session_name']} ✓{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}SESSION: {session['session_name']}{Style.RESET_ALL}")
            if session['next_open_ist']:
                print(f"{Fore.CYAN}NEXT OPEN: {session['next_open_ist']}{Style.RESET_ALL}")
    
    if result['signal'] != "WAIT":
        print(f"CONFIDENCE: {result['confidence']}%")
        print(f"PRICE: {result['price']}")
        print(f"STOP-LOSS: {result['stop_loss']}")
        print(f"TAKE-PROFIT: {result['take_profit']}")
        print(f"REASON: {result['reason']}")
    else:
        print(f"PRICE: {result['price']}")
        print(f"REASON: {result['reason']}")
    
    # Show detected chart patterns with bias
    if 'patterns' in result and result['patterns']:
        print(f"\n{Fore.MAGENTA}📊 CHART PATTERNS DETECTED:{Style.RESET_ALL}")
        for pattern in result['patterns']:
            if 'Bullish' in pattern:
                print(f"  {Fore.GREEN}▲ {pattern}{Style.RESET_ALL}")
            elif 'Bearish' in pattern:
                print(f"  {Fore.RED}▼ {pattern}{Style.RESET_ALL}")
            else:
                print(f"  {Fore.YELLOW}◆ {pattern}{Style.RESET_ALL}")
        
        # Show pattern score impact
        if 'pattern_score' in result and result['pattern_score'] != 0:
            print(f"{Fore.CYAN}Pattern Score Contribution: {result['pattern_score']:+.1f}{Style.RESET_ALL}")
    
    print(f"----------------------------------------{Style.RESET_ALL}\n")

def interactive_mode():
    print(f"{Fore.GREEN}Forex AI Decision Engine - Interactive Mode{Style.RESET_ALL}")
    print("Background monitor is active (fetching news, logging core signals).")
    print("Type a symbol (e.g., EURUSD, BTCUSD, AAPL) to analyze immediately.")
    print("Type 'exit' to quit.\n")
    
    engine = DecisionEngine()
    
    while True:
        try:
            user_input = input(f"{Fore.CYAN}Enter Symbol > {Style.RESET_ALL}").strip().upper()
            if not user_input:
                continue
            if user_input == "EXIT":
                print("Shutting down...")
                sys.exit(0)
            
            # Check if valid symbol
            if user_input not in Config.PAIRS + Config.VALID_SYMBOLS:
                print(f"{Fore.RED}✗ Invalid Symbol: '{user_input}' not recognized{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Valid symbols: {', '.join(Config.VALID_SYMBOLS[:15])}...{Style.RESET_ALL}")
                continue
            
            print(f"Fetching data for {user_input}...")
            result = engine.analyze_pair(user_input)
            
            # Immediate Price Output
            if result['price'] > 0:
                 print(f"\n{Fore.CYAN}>>> Current Price ({user_input}): {Style.BRIGHT}{result['price']}{Style.RESET_ALL}")
            
            print_report(result)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
        except EOFError:
            print(f"{Fore.YELLOW}\nNon-interactive mode detected (EOF). Switching to background-only mode.{Style.RESET_ALL}")
            while True:
                time.sleep(60)
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

def main():
    print("Starting Core Engine v1.2 (Interactive/Headless Fix)...")
    sys.stdout.flush()
    # Check for valid API keys
    check_api_keys()
    
    init_db()
    
    # 1. Run initial data fetch
    print("Initializing Data & Sentiment (Please wait)...")
    run_analysis_cycle(mode="init")
    
    # 2. Start Background Thread
    t = threading.Thread(target=background_job, daemon=True)
    t.start()
    
    # 3. Enter Interactive Mode if TTY is present
    if sys.stdin.isatty():
        interactive_mode()
    else:
        print("Running in headless mode. Background job is active.")
        # Keep main thread alive
        while True:
            time.sleep(60)

if __name__ == "__main__":
    main()
