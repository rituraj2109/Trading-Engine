"""
Verify Data Storage - Check what's being saved every 15 minutes
"""
import sqlite3
from config import Config
from datetime import datetime, timedelta

def verify_storage():
    print("\n" + "="*70)
    print("DATA STORAGE VERIFICATION")
    print("="*70)
    
    try:
        conn = sqlite3.connect(Config.DB_FILE)
        cursor = conn.cursor()
        
        # Check Market Data (with indicators)
        print("\n📊 MARKET DATA & INDICATORS (15-min candles):")
        print("-"*70)
        cursor.execute('''
            SELECT pair, COUNT(*) as records, MAX(time) as latest_time
            FROM market_data 
            GROUP BY pair 
            ORDER BY pair
        ''')
        market_data = cursor.fetchall()
        
        if market_data:
            print(f"{'Symbol':<10} {'Records':<10} {'Latest Update (UTC)':<30}")
            print("-"*70)
            for row in market_data:
                pair, count, latest = row
                print(f"{pair:<10} {count:<10} {latest:<30}")
            
            # Show sample of latest data with indicators
            print("\n📈 LATEST INDICATOR VALUES (Most Recent):")
            print("-"*70)
            cursor.execute('''
                SELECT pair, time, close, rsi, macd, atr, ema_20, ema_50
                FROM market_data 
                ORDER BY time DESC 
                LIMIT 5
            ''')
            latest_data = cursor.fetchall()
            for row in latest_data:
                pair, time, close, rsi, macd, atr, ema20, ema50 = row
                print(f"\n{pair} @ {time}")
                print(f"  Price: {close:.5f}")
                print(f"  RSI: {rsi:.2f}, MACD: {macd:.5f}, ATR: {atr:.5f}")
                print(f"  EMA20: {ema20:.5f}, EMA50: {ema50:.5f}")
        else:
            print("❌ No market data found yet")
        
        # Check Signals
        print("\n\n🎯 SIGNALS (All signals including WAIT):")
        print("-"*70)
        cursor.execute('''
            SELECT pair, COUNT(*) as records, MAX(time) as latest_time
            FROM signals 
            GROUP BY pair 
            ORDER BY pair
        ''')
        signals_data = cursor.fetchall()
        
        if signals_data:
            print(f"{'Symbol':<10} {'Records':<10} {'Latest Signal (IST)':<30}")
            print("-"*70)
            for row in signals_data:
                pair, count, latest = row
                print(f"{pair:<10} {count:<10} {latest:<30}")
            
            # Show recent signals
            print("\n🔔 RECENT SIGNALS:")
            print("-"*70)
            cursor.execute('''
                SELECT time, pair, signal, confidence, entry_price, reason
                FROM signals 
                ORDER BY time DESC 
                LIMIT 10
            ''')
            recent_signals = cursor.fetchall()
            for row in recent_signals:
                time, pair, signal, conf, price, reason = row
                signal_icon = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "⚪"
                print(f"{signal_icon} {pair:<8} {signal:<5} {conf:>5.1f}% @ {price:.5f} | {reason[:40]}")
        else:
            print("❌ No signals found yet")
        
        # Check News
        print("\n\n📰 NEWS DATA:")
        print("-"*70)
        cursor.execute('SELECT COUNT(*) as total FROM news')
        news_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT MAX(date) as latest FROM news')
        latest_news = cursor.fetchone()[0]
        
        print(f"Total News Articles: {news_count}")
        print(f"Latest News Date: {latest_news}")
        
        if news_count > 0:
            cursor.execute('''
                SELECT date, title, source, sentiment_score 
                FROM news 
                ORDER BY date DESC 
                LIMIT 5
            ''')
            recent_news = cursor.fetchall()
            print("\n📰 Recent News (with sentiment):")
            print("-"*70)
            for row in recent_news:
                date, title, source, sentiment = row
                sentiment_str = f"{sentiment:+.3f}" if sentiment else "0.000"
                print(f"{source:<12} [{sentiment_str}] {title[:50]}")
        
        conn.close()
        
        # Summary
        print("\n" + "="*70)
        print("✅ VERIFICATION SUMMARY:")
        print("="*70)
        
        if market_data and len(market_data) > 0:
            print("✓ Market data with indicators is being stored")
            print(f"  → {len(market_data)} symbols tracked")
            print(f"  → Includes: OHLC, RSI, MACD, ATR, EMA20, EMA50")
        else:
            print("⚠ No market data yet - wait for first 15-min cycle")
        
        if signals_data and len(signals_data) > 0:
            print("✓ Signals are being stored (BUY/SELL/WAIT)")
            print(f"  → {len(signals_data)} symbols tracked")
        else:
            print("⚠ No signals yet - wait for first 15-min cycle")
        
        if news_count > 0:
            print(f"✓ News data is being stored ({news_count} articles)")
            print("  → Includes sentiment analysis")
        else:
            print("⚠ No news yet - wait for first fetch")
        
        print("\n🔄 Background task runs every 15 minutes")
        print("📊 All data is stored in: forex_engine.db")
        print("="*70 + "\n")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_storage()
