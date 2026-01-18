"""
DEPLOYMENT VERIFICATION SCRIPT
====================================
This script verifies that your forex trading engine is ready for production deployment.
It checks all critical components before you deploy.
"""

import sys
import os
from datetime import datetime, timedelta
from colorama import Fore, Style, init

init(autoreset=True)

def print_header(text):
    print(f"\n{Style.BRIGHT}{'='*70}")
    print(f"{text}")
    print(f"{'='*70}{Style.RESET_ALL}")

def print_success(text):
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

def print_warning(text):
    print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.CYAN}ℹ {text}{Style.RESET_ALL}")

def check_dependencies():
    """Check if all required packages are installed"""
    print_header("1. CHECKING DEPENDENCIES")
    
    required_packages = [
        'pandas', 'numpy', 'requests', 'ta', 'vaderSentiment',
        'schedule', 'dotenv', 'colorama', 'sqlite3'
    ]
    
    all_good = True
    for package in required_packages:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            elif package == 'vaderSentiment':
                __import__('vaderSentiment')
            else:
                __import__(package)
            print_success(f"{package} installed")
        except ImportError:
            print_error(f"{package} NOT installed")
            all_good = False
    
    return all_good

def check_config():
    """Check configuration and API keys"""
    print_header("2. CHECKING CONFIGURATION")
    
    try:
        from config import Config
        
        # Check API keys
        print("\n📋 API Key Status:")
        api_keys = {
            'TwelveData': Config.API_KEY_TWELVEDATA,
            'NewsAPI': Config.API_KEY_NEWSAPI,
            'Finnhub': Config.API_KEY_FINNHUB,
            'FMP': Config.API_KEY_FMP,
        }
        
        demo_keys = 0
        for name, key in api_keys.items():
            if key == "DEMO_KEY":
                print_warning(f"{name}: Using DEMO_KEY (limited functionality)")
                demo_keys += 1
            else:
                print_success(f"{name}: Configured")
        
        if demo_keys > 0:
            print_warning(f"\n{demo_keys} API key(s) using DEMO_KEY - get real keys for full functionality")
        
        # Check trading pairs
        print(f"\n📊 Trading Pairs: {len(Config.PAIRS)}")
        print(f"   {', '.join(Config.PAIRS)}")
        
        # Check timeframe
        print(f"\n⏱ Timeframe: {Config.TIMEFRAME}")
        if Config.TIMEFRAME == "15min":
            print_success("15-minute interval configured correctly")
        else:
            print_warning(f"Timeframe is {Config.TIMEFRAME}, expected 15min")
        
        # Check risk parameters
        print(f"\n💰 Risk Management:")
        print(f"   Risk per trade: {Config.RISK_PERCENT*100}%")
        print(f"   Min Risk:Reward: 1:{Config.MIN_RISK_REWARD}")
        print(f"   ATR SL Multiplier: {Config.ATR_MULTIPLIER_SL}")
        
        # Check thresholds
        print(f"\n🎯 Signal Thresholds:")
        print(f"   BUY threshold: {Config.BUY_THRESHOLD}")
        print(f"   SELL threshold: {Config.SELL_THRESHOLD}")
        
        return True
        
    except Exception as e:
        print_error(f"Config check failed: {e}")
        return False

def check_database():
    """Check database structure"""
    print_header("3. CHECKING DATABASE")
    
    try:
        from utils import init_db, get_db_connection
        
        # Initialize DB if not exists
        init_db()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['news', 'signals', 'market_data', 'pattern_history']
        for table in required_tables:
            if table in tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                print_success(f"Table '{table}' exists ({count} records)")
            else:
                print_error(f"Table '{table}' missing")
                conn.close()
                return False
        
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"Database check failed: {e}")
        return False

def test_data_fetch():
    """Test if data fetching works"""
    print_header("4. TESTING DATA FETCHING")
    
    try:
        from data_loader import DataLoader
        
        loader = DataLoader()
        
        # Test market data fetch
        print("\n📈 Testing market data fetch (EURUSD)...")
        df = loader.fetch_market_data("EURUSD")
        
        if df is not None and len(df) > 0:
            print_success(f"Market data fetched: {len(df)} candles")
            print(f"   Latest price: {df.iloc[-1]['close']:.5f}")
            print(f"   Timeframe: {df.index[-1] if hasattr(df, 'index') else 'N/A'}")
        else:
            print_error("Failed to fetch market data")
            return False
        
        # Test news fetch
        print("\n📰 Testing news fetch...")
        try:
            loader.fetch_all_news()
            print_success("News fetch completed")
        except Exception as e:
            print_warning(f"News fetch warning: {e}")
        
        return True
        
    except Exception as e:
        print_error(f"Data fetch test failed: {e}")
        return False

def test_indicators():
    """Test indicator calculations"""
    print_header("5. TESTING TECHNICAL INDICATORS")
    
    try:
        from data_loader import DataLoader
        from indicators import TechnicalAnalysis
        
        loader = DataLoader()
        ta = TechnicalAnalysis()
        
        print("\n📊 Testing indicators on EURUSD...")
        df = loader.fetch_market_data("EURUSD")
        
        if df is None or len(df) < 50:
            print_error("Insufficient data for indicators")
            return False
        
        df = ta.add_indicators(df)
        latest = df.iloc[-1]
        
        indicators = ['rsi', 'macd', 'atr', 'ema_20', 'ema_50']
        for ind in indicators:
            if ind in latest and latest[ind] is not None:
                print_success(f"{ind.upper()}: {latest[ind]:.5f}")
            else:
                print_error(f"{ind.upper()} not calculated")
                return False
        
        return True
        
    except Exception as e:
        print_error(f"Indicator test failed: {e}")
        return False

def test_signal_generation():
    """Test signal generation"""
    print_header("6. TESTING SIGNAL GENERATION")
    
    try:
        from strategy import DecisionEngine
        
        engine = DecisionEngine()
        
        print("\n🎯 Generating signal for EURUSD...")
        result = engine.analyze_pair("EURUSD")
        
        if result:
            print_success("Signal generated successfully")
            print(f"   Signal: {result['signal']}")
            print(f"   Confidence: {result['confidence']}%")
            print(f"   Price: {result['price']}")
            print(f"   Stop Loss: {result['stop_loss']}")
            print(f"   Take Profit: {result['take_profit']}")
            print(f"   Reason: {result['reason']}")
            
            if 'session_info' in result:
                session = result['session_info']
                status = "OPEN" if session['is_open'] else "CLOSED"
                print(f"   Session: {status} - {session['session_name']}")
        else:
            print_error("Signal generation failed")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Signal generation test failed: {e}")
        return False

def test_15min_cycle():
    """Test complete 15-minute cycle"""
    print_header("7. TESTING 15-MINUTE CYCLE")
    
    try:
        from config import Config
        from utils import get_db_connection
        from strategy import DecisionEngine
        import time
        
        print(f"\n🔄 Running full cycle for {len(Config.PAIRS)} pairs...")
        
        engine = DecisionEngine()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        saved_count = 0
        signal_count = 0
        
        for i, pair in enumerate(Config.PAIRS, 1):
            print(f"\n[{i}/{len(Config.PAIRS)}] Processing {pair}...")
            
            try:
                # Rate limiting
                if i > 1:
                    time.sleep(2)
                
                result = engine.analyze_pair(pair)
                
                # Try to save to database
                if 'raw_data' in result:
                    rd = result['raw_data']
                    cursor.execute('''
                        INSERT OR REPLACE INTO market_data (time, pair, open, high, low, close, rsi, macd, atr, ema_20, ema_50)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (str(rd['time']), pair, rd['open'], rd['high'], rd['low'], rd['close'], 
                          rd['rsi'], rd['macd'], rd['atr'], rd['ema_20'], rd['ema_50']))
                    saved_count += 1
                
                cursor.execute('''
                    INSERT INTO signals (time, pair, signal, confidence, entry_price, stop_loss, take_profit, reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (str(result['time']), pair, result['signal'], result['confidence'], 
                      result['price'], result['stop_loss'], result['take_profit'], result['reason']))
                signal_count += 1
                
                conn.commit()
                print_success(f"{pair}: {result['signal']} ({result['confidence']}%)")
                
            except Exception as e:
                print_error(f"{pair}: {e}")
        
        conn.close()
        
        print(f"\n✓ Cycle complete:")
        print(f"   Market data saved: {saved_count}/{len(Config.PAIRS)}")
        print(f"   Signals saved: {signal_count}/{len(Config.PAIRS)}")
        
        return saved_count > 0 and signal_count > 0
        
    except Exception as e:
        print_error(f"15-minute cycle test failed: {e}")
        return False

def check_continuous_loop():
    """Check if schedule is configured correctly"""
    print_header("8. CHECKING CONTINUOUS LOOP SETUP")
    
    try:
        import schedule
        
        print("\n⏰ Schedule Configuration:")
        print_success("schedule library available")
        
        # Check main.py structure
        print("\n📄 Checking main.py structure...")
        with open('main.py', 'r') as f:
            content = f.read()
            
            checks = [
                ('schedule.every(15).minutes', '15-minute interval'),
                ('threading.Thread', 'Background thread'),
                ('daemon=True', 'Daemon thread'),
                ('run_analysis_cycle', 'Analysis cycle function'),
            ]
            
            for check, desc in checks:
                if check in content:
                    print_success(f"{desc} configured")
                else:
                    print_warning(f"{desc} not found")
        
        return True
        
    except Exception as e:
        print_error(f"Loop check failed: {e}")
        return False

def generate_accuracy_report():
    """Generate accuracy report from historical signals"""
    print_header("9. ACCURACY ANALYSIS")
    
    try:
        from utils import get_db_connection
        import pandas as pd
        
        conn = get_db_connection()
        
        # Get signals
        signals_df = pd.read_sql_query('SELECT * FROM signals', conn)
        
        if len(signals_df) == 0:
            print_warning("No historical signals to analyze yet")
            print_info("Accuracy will be calculated after collecting data")
            conn.close()
            return True
        
        # Get market data
        market_df = pd.read_sql_query('SELECT * FROM market_data', conn)
        conn.close()
        
        print(f"\n📊 Total Signals: {len(signals_df)}")
        
        # Count by signal type
        signal_counts = signals_df['signal'].value_counts()
        print("\n📈 Signal Distribution:")
        for signal, count in signal_counts.items():
            percentage = (count / len(signals_df)) * 100
            print(f"   {signal}: {count} ({percentage:.1f}%)")
        
        # Average confidence
        avg_confidence = signals_df['confidence'].mean()
        print(f"\n🎯 Average Confidence: {avg_confidence:.2f}%")
        
        # Pair distribution
        pair_counts = signals_df['pair'].value_counts()
        print(f"\n💱 Most Active Pairs:")
        for pair, count in pair_counts.head(5).items():
            print(f"   {pair}: {count} signals")
        
        print_info("\nNote: Real accuracy calculation requires tracking signal outcomes")
        print_info("Deploy and run for at least 24-48 hours to calculate meaningful accuracy")
        
        return True
        
    except Exception as e:
        print_error(f"Accuracy analysis failed: {e}")
        return False

def final_deployment_checklist():
    """Final checklist before deployment"""
    print_header("10. FINAL DEPLOYMENT CHECKLIST")
    
    checklist = [
        "✓ All dependencies installed",
        "✓ Configuration verified",
        "✓ Database initialized",
        "✓ Data fetching works",
        "✓ Indicators calculating correctly",
        "✓ Signals generating",
        "✓ 15-minute cycle tested",
        "✓ Continuous loop configured",
    ]
    
    for item in checklist:
        print(f"{Fore.GREEN}{item}{Style.RESET_ALL}")
    
    print(f"\n{Style.BRIGHT}DEPLOYMENT READY!{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}To deploy and run continuously:{Style.RESET_ALL}")
    print(f"  1. On Windows: python main.py")
    print(f"  2. On VPS (Linux): nohup python main.py > output.log 2>&1 &")
    print(f"  3. Or use screen/tmux: screen -S forex && python main.py")
    
    print(f"\n{Fore.CYAN}What will happen:{Style.RESET_ALL}")
    print(f"  • Initial data fetch at startup")
    print(f"  • Every 15 minutes: fetch news, update sentiment, analyze all pairs")
    print(f"  • Market data + indicators saved to database")
    print(f"  • BUY/SELL signals logged with confidence, entry, SL, TP")
    print(f"  • Only active market hours considered for trading")
    
    print(f"\n{Fore.CYAN}Monitoring:{Style.RESET_ALL}")
    print(f"  • Check logs: tail -f trading_engine.log")
    print(f"  • View data: python show_saved_data.py")
    print(f"  • Generate reports: python generate_report.py")
    
    print(f"\n{Fore.YELLOW}⚠ IMPORTANT:{Style.RESET_ALL}")
    print(f"  • API rate limits: Monitor for 429 errors")
    print(f"  • First 24-48 hours: Collect data for accuracy baseline")
    print(f"  • Accuracy improves over time with more data")
    print(f"  • This is a SIGNAL GENERATOR, not an auto-trader")
    print(f"  • Always verify signals before executing trades")

def main():
    print(f"\n{Style.BRIGHT}{Fore.CYAN}")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║          FOREX ENGINE - DEPLOYMENT VERIFICATION                  ║")
    print("║                                                                  ║")
    print("║  This will verify all components before deployment              ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")
    
    tests = [
        ("Dependencies", check_dependencies),
        ("Configuration", check_config),
        ("Database", check_database),
        ("Data Fetching", test_data_fetch),
        ("Indicators", test_indicators),
        ("Signal Generation", test_signal_generation),
        ("15-Min Cycle", test_15min_cycle),
        ("Continuous Loop", check_continuous_loop),
        ("Accuracy Analysis", generate_accuracy_report),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            
            if not result:
                print_error(f"\n{name} check FAILED")
        except Exception as e:
            print_error(f"\n{name} check FAILED with exception: {e}")
            results.append((name, False))
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n{Style.BRIGHT}Tests Passed: {passed}/{total}{Style.RESET_ALL}")
    
    for name, result in results:
        if result:
            print_success(f"{name}")
        else:
            print_error(f"{name}")
    
    if passed == total:
        print(f"\n{Style.BRIGHT}{Fore.GREEN}✓ ALL CHECKS PASSED - READY FOR DEPLOYMENT!{Style.RESET_ALL}")
        final_deployment_checklist()
        return 0
    else:
        print(f"\n{Style.BRIGHT}{Fore.RED}✗ SOME CHECKS FAILED - FIX ISSUES BEFORE DEPLOYMENT{Style.RESET_ALL}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
