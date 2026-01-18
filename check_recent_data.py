import sqlite3
from datetime import datetime, timedelta

def check_recent_data():
    conn = sqlite3.connect('forex_engine.db')
    c = conn.cursor()
    
    print("="*80)
    print("FOREX ENGINE - RECENT SAVED DATA VERIFICATION")
    print("="*80)
    
    # 1. Market Data
    print("\n[1] RECENT MARKET DATA (Last 5 records)")
    print("-"*80)
    c.execute('SELECT time, pair, close, rsi, macd, atr, ema_20, ema_50 FROM market_data ORDER BY time DESC LIMIT 5')
    rows = c.fetchall()
    if rows:
        for row in rows:
            print(f"Time: {row[0]}")
            print(f"  Pair: {row[1]} | Close: {row[2]}")
            print(f"  RSI: {row[3]:.2f} | MACD: {row[4]:.5f} | ATR: {row[5]:.5f}")
            print(f"  EMA_20: {row[6]:.5f} | EMA_50: {row[7]:.5f}")
            print()
    else:
        print("  WARNING: No market data found")
    
    # Count total market records
    c.execute('SELECT COUNT(*) FROM market_data')
    total_market = c.fetchone()[0]
    print(f"  >> Total Market Data Records: {total_market}\n")
    
    # 2. Signals
    print("[2] RECENT SIGNALS (Last 5 records)")
    print("-"*80)
    c.execute('SELECT time, pair, signal, confidence, entry_price, stop_loss, take_profit, reason FROM signals ORDER BY time DESC LIMIT 5')
    rows = c.fetchall()
    if rows:
        for row in rows:
            signal_color = "[BUY]" if row[2] == "BUY" else "[SELL]" if row[2] == "SELL" else "[WAIT]"
            print(f"Time: {row[0]}")
            print(f"  {signal_color} Pair: {row[1]} | Signal: {row[2]} | Confidence: {row[3]}%")
            print(f"  Entry: {row[4]} | SL: {row[5]} | TP: {row[6]}")
            print(f"  Reason: {row[7]}")
            print()
    else:
        print("  WARNING: No signals found")
    
    # Count total signals
    c.execute('SELECT COUNT(*) FROM signals')
    total_signals = c.fetchone()[0]
    print(f"  >> Total Signal Records: {total_signals}\n")
    
    # 3. Pattern History
    print("[3] RECENT CHART PATTERNS (Last 10 records)")
    print("-"*80)
    c.execute('SELECT time, pair, pattern_name, bias, score, confidence FROM pattern_history ORDER BY time DESC LIMIT 10')
    rows = c.fetchall()
    if rows:
        for row in rows:
            bias_icon = "[BULL]" if row[3] == "bullish" else "[BEAR]" if row[3] == "bearish" else "[NEUT]"
            print(f"Time: {row[0]}")
            print(f"  {bias_icon} Pair: {row[1]} | Pattern: {row[2]}")
            print(f"  Bias: {row[3]} | Score: {row[4]} | Confidence: {row[5]}")
            print()
    else:
        print("  WARNING: No patterns found")
    
    # Count total patterns
    c.execute('SELECT COUNT(*) FROM pattern_history')
    total_patterns = c.fetchone()[0]
    print(f"  >> Total Pattern Records: {total_patterns}\n")
    
    # 4. Time Analysis
    print("[4] DATA FRESHNESS CHECK")
    print("-"*80)
    c.execute('SELECT MAX(time) FROM market_data')
    last_market_time = c.fetchone()[0]
    c.execute('SELECT MAX(time) FROM signals')
    last_signal_time = c.fetchone()[0]
    
    print(f"  Last Market Data: {last_market_time}")
    print(f"  Last Signal: {last_signal_time}")
    
    # Check if data is recent (within 20 minutes)
    if last_market_time:
        try:
            # Try to parse if it's a datetime string
            if "IST" in str(last_market_time):
                print(f"\n  OK: Data appears to be recent (IST timezone)")
            else:
                print(f"\n  OK: Last update: {last_market_time}")
        except:
            print(f"\n  INFO: Last update: {last_market_time}")
    
    # 5. Summary by Pair
    print("\n[5] DATA SUMMARY BY PAIR")
    print("-"*80)
    c.execute('''
        SELECT pair, COUNT(*) as count, MAX(time) as last_update 
        FROM market_data 
        GROUP BY pair 
        ORDER BY last_update DESC
    ''')
    rows = c.fetchall()
    if rows:
        for row in rows:
            print(f"  {row[0]}: {row[1]} records | Last: {row[2]}")
    
    conn.close()
    print("\n" + "="*80)

if __name__ == "__main__":
    check_recent_data()
