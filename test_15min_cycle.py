"""
Test 15-Minute Data Storage Cycle
This simulates one background cycle to verify everything is saved correctly
"""
from config import Config
from utils import init_db, logger, get_db_connection
from data_loader import DataLoader
from sentiment import SentimentEngine
from strategy import DecisionEngine
import time

def test_15min_cycle():
    print("\n" + "="*70)
    print("🔄 TESTING 15-MINUTE DATA STORAGE CYCLE")
    print("="*70)
    
    # Initialize database
    init_db()
    
    print("\n📋 This test will:")
    print("  1. Fetch news from all sources")
    print("  2. Update sentiment scores")
    print("  3. Fetch market data for all 7 symbols")
    print("  4. Calculate indicators (RSI, MACD, ATR, EMAs)")
    print("  5. Store everything in database")
    print("\n⏳ Starting cycle...\n")
    
    # 1. Fetch News
    print("="*70)
    print("STEP 1: FETCHING NEWS")
    print("="*70)
    loader = DataLoader()
    print("Fetching from FMP, NewsAPI, Finnhub...")
    loader.fetch_all_news()
    
    # 2. Update Sentiment
    print("\n" + "="*70)
    print("STEP 2: UPDATING SENTIMENT SCORES")
    print("="*70)
    sentiment = SentimentEngine()
    sentiment.update_sentiment_scores()
    print("✓ Sentiment analysis complete")
    
    # 3. Process All Pairs
    print("\n" + "="*70)
    print(f"STEP 3: PROCESSING {len(Config.PAIRS)} SYMBOLS")
    print("="*70)
    print(f"Symbols: {', '.join(Config.PAIRS)}\n")
    
    engine = DecisionEngine()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    market_data_saved = 0
    signals_saved = 0
    
    for i, pair in enumerate(Config.PAIRS, 1):
        print(f"\n[{i}/{len(Config.PAIRS)}] Processing {pair}...")
        
        try:
            # Small delay for rate limiting
            if i > 1:
                time.sleep(2)
            
            # Analyze pair
            result = engine.analyze_pair(pair)
            
            # Save Market Data & Indicators
            if 'raw_data' in result:
                rd = result['raw_data']
                cursor.execute('''
                    INSERT OR REPLACE INTO market_data (time, pair, open, high, low, close, rsi, macd, atr, ema_20, ema_50)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (str(rd['time']), pair, rd['open'], rd['high'], rd['low'], rd['close'], 
                      rd['rsi'], rd['macd'], rd['atr'], rd['ema_20'], rd['ema_50']))
                conn.commit()
                market_data_saved += 1
                
                print(f"  ✓ Market Data: Close={result['price']:.5f}")
                print(f"  ✓ Indicators: RSI={rd['rsi']:.2f}, MACD={rd['macd']:.5f}, ATR={rd['atr']:.5f}")
                print(f"  ✓ EMAs: EMA20={rd['ema_20']:.5f}, EMA50={rd['ema_50']:.5f}")
            
            # Save Signal
            cursor.execute('''
                INSERT INTO signals (time, pair, signal, confidence, entry_price, stop_loss, take_profit, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (str(result['time']), pair, result['signal'], result['confidence'], 
                  result['price'], result['stop_loss'], result['take_profit'], result['reason']))
            conn.commit()
            signals_saved += 1
            
            # Show session info
            if 'session_info' in result:
                session = result['session_info']
                status = "🟢 OPEN" if session['is_open'] else "🔴 CLOSED"
                print(f"  ✓ Session: {status} - {session['session_name']}")
                if not session['is_open'] and session['next_open_ist']:
                    print(f"    Next Open: {session['next_open_ist']}")
            
            print(f"  ✓ Signal: {result['signal']} (Confidence: {result['confidence']}%)")
            print(f"  ✓ Reason: {result['reason']}")
            
            # Show detected patterns
            if 'patterns' in result and result['patterns']:
                print(f"  📊 Patterns: {', '.join(result['patterns'])}")
                if 'pattern_score' in result:
                    print(f"     Pattern Score: {result['pattern_score']:+.1f}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    conn.close()
    
    # Summary
    print("\n" + "="*70)
    print("✅ CYCLE COMPLETE - SUMMARY")
    print("="*70)
    print(f"✓ Market Data Records Saved: {market_data_saved}")
    print(f"  → Each record contains: OHLC + RSI + MACD + ATR + EMA20 + EMA50")
    print(f"✓ Signal Records Saved: {signals_saved}")
    print(f"  → Includes BUY/SELL/WAIT signals with entry/SL/TP")
    print(f"✓ News Articles: Check database for latest count")
    
    # Quick database check
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM market_data')
    total_market_records = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM signals')
    total_signals = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM news')
    total_news = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n📊 TOTAL DATABASE RECORDS:")
    print(f"  • Market Data: {total_market_records} records")
    print(f"  • Signals: {total_signals} records")
    print(f"  • News: {total_news} articles")
    
    print("\n🔄 In production, this cycle runs automatically every 15 minutes")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_15min_cycle()
