"""
Monitor 15-Minute Cycle - Check if data is updating regularly
"""
import sqlite3
import pandas as pd
from datetime import datetime, timezone, timedelta

from config import Config
DB = Config.DB_FILE

print("\n" + "="*70)
print("15-MINUTE CYCLE STATUS CHECK")
print("="*70)

conn = sqlite3.connect(DB)

# Current time
now_utc = datetime.now(timezone.utc)
print(f"\nCurrent Time (UTC): {now_utc.strftime('%Y-%m-%d %H:%M:%S')}")

# 1. Check Market Data + Indicators
print("\n" + "-"*70)
print("📊 MARKET DATA & INDICATORS")
print("-"*70)

market_df = pd.read_sql_query('SELECT * FROM market_data ORDER BY time DESC LIMIT 50', conn)
if not market_df.empty:
    market_df['time_parsed'] = pd.to_datetime(market_df['time'], utc=True, format='ISO8601', errors='coerce')
    
    latest = market_df['time_parsed'].max()
    age_minutes = (now_utc - latest.to_pydatetime().replace(tzinfo=timezone.utc)).total_seconds() / 60
    
    print(f"Latest Update: {latest} UTC")
    print(f"Age: {age_minutes:.1f} minutes")
    
    if age_minutes < 0:
        print("⚠️  WARNING: System clock is behind database time")
        age_minutes = abs(age_minutes)
    
    if age_minutes <= 15:
        print("✅ Status: ACTIVE (updated within last 15 minutes)")
    elif age_minutes <= 30:
        print("⚠️  Status: DELAYED (last update 15-30 minutes ago)")
    else:
        print("❌ Status: INACTIVE (no updates for >30 minutes)")
    
    # Show recent updates per pair
    recent = market_df.head(20)
    print(f"\nRecent Updates (last 20):")
    for _, row in recent.iterrows():
        print(f"  {row['pair']}: {row['time']} (RSI: {row['rsi']:.1f}, MACD: {row['macd']:.5f})")
    
    # Check if updates are on 15-min intervals
    print("\nUpdate Intervals:")
    recent_times = market_df[market_df['pair'] == 'EURUSD']['time_parsed'].head(10).sort_values()
    if len(recent_times) > 1:
        intervals = recent_times.diff().dt.total_seconds() / 60
        intervals = intervals.dropna()
        if len(intervals) > 0:
            avg_interval = intervals.mean()
            print(f"  Average interval: {avg_interval:.1f} minutes")
            if 14 <= avg_interval <= 16:
                print("  ✅ Updates happening every ~15 minutes")
            else:
                print(f"  ⚠️  Updates not on 15-min schedule (averaging {avg_interval:.1f} min)")
else:
    print("❌ No market data found")

# 2. Check Signals
print("\n" + "-"*70)
print("🎯 TRADING SIGNALS")
print("-"*70)

sig_df = pd.read_sql_query('SELECT * FROM signals ORDER BY rowid DESC LIMIT 50', conn)
if not sig_df.empty:
    sig_df['time_parsed'] = pd.to_datetime(sig_df['time'], utc=True, format='ISO8601', errors='coerce')
    
    latest = sig_df['time_parsed'].max()
    age_minutes = abs((now_utc - latest.to_pydatetime().replace(tzinfo=timezone.utc)).total_seconds() / 60)
    
    print(f"Latest Signal: {latest} UTC")
    print(f"Age: {age_minutes:.1f} minutes")
    
    if age_minutes <= 15:
        print("✅ Status: ACTIVE")
    else:
        print("⚠️  Status: Last signal >15 minutes ago")
    
    # Show recent signals
    print(f"\nRecent Signals (last 10):")
    for _, row in sig_df.head(10).iterrows():
        time_str = row['time'][:19] if len(str(row['time'])) > 19 else row['time']
        print(f"  {row['pair']}: {row['signal']} @ {time_str} (Conf: {row['confidence']:.1f}%)")
else:
    print("❌ No signals found")

# 3. Check Chart Patterns
print("\n" + "-"*70)
print("📈 CHART PATTERNS")
print("-"*70)

pattern_df = pd.read_sql_query('SELECT * FROM pattern_history ORDER BY rowid DESC LIMIT 20', conn)
if not pattern_df.empty:
    pattern_df['time_parsed'] = pd.to_datetime(pattern_df['time'], utc=True, format='ISO8601', errors='coerce')
    
    latest = pattern_df['time_parsed'].max()
    age_minutes = abs((now_utc - latest.to_pydatetime().replace(tzinfo=timezone.utc)).total_seconds() / 60)
    
    print(f"Latest Pattern: {latest} UTC")
    print(f"Age: {age_minutes:.1f} minutes")
    print(f"Total Patterns Detected: {len(pattern_df)}")
    
    if age_minutes <= 15:
        print("✅ Status: ACTIVE")
    else:
        print("⚠️  Status: No new patterns in last 15 minutes")
    
    # Show recent patterns
    print(f"\nRecent Patterns (last 10):")
    for _, row in pattern_df.head(10).iterrows():
        time_str = row['time'][:19] if len(str(row['time'])) > 19 else row['time']
        print(f"  {row['pair']}: {row['pattern_name']} ({row['bias']}) @ {time_str}")
else:
    print("⚠️  No chart patterns detected yet")

# 4. Check News
print("\n" + "-"*70)
print("📰 NEWS")
print("-"*70)

news_df = pd.read_sql_query('SELECT * FROM news ORDER BY date DESC LIMIT 20', conn)
if not news_df.empty:
    try:
        news_df['date_parsed'] = pd.to_datetime(news_df['date'], utc=True, errors='coerce')
        latest = news_df['date_parsed'].max()
        age_hours = (now_utc - latest.to_pydatetime().replace(tzinfo=timezone.utc)).total_seconds() / 3600
        
        print(f"Latest News: {latest} UTC")
        print(f"Age: {age_hours:.1f} hours")
        print(f"Total News Articles: {len(news_df)}")
        
        if age_hours <= 1:
            print("✅ Status: FRESH (updated within last hour)")
        elif age_hours <= 24:
            print("⚠️  Status: STALE (last update {:.1f} hours ago)".format(age_hours))
        else:
            print("❌ Status: OLD (last update {:.1f} hours ago)".format(age_hours))
        
        # Show recent news
        print(f"\nRecent News (last 5):")
        for _, row in news_df.head(5).iterrows():
            date_str = str(row['date'])[:19] if len(str(row['date'])) > 19 else row['date']
            print(f"  [{row['source']}] {row['title'][:60]}... ({date_str})")
    except Exception as e:
        print(f"⚠️  Error parsing news dates: {e}")
else:
    print("❌ No news found")

conn.close()

# 5. Overall Status
print("\n" + "="*70)
print("OVERALL STATUS")
print("="*70)

# Determine if engine is running
if not market_df.empty:
    latest_market = market_df['time_parsed'].max()
    market_age = abs((now_utc - latest_market.to_pydatetime().replace(tzinfo=timezone.utc)).total_seconds() / 60)
    
    if market_age <= 15:
        print("✅ 15-MINUTE CYCLE: RUNNING")
        print("   → Market data updating")
        print("   → Indicators calculating")
        print("   → Signals generating")
        print("\n   Engine is operational and saving data every 15 minutes")
    elif market_age <= 30:
        print("⚠️  15-MINUTE CYCLE: DELAYED")
        print(f"   Last update was {market_age:.1f} minutes ago")
        print("   → Check if engine is still running")
    else:
        print("❌ 15-MINUTE CYCLE: NOT RUNNING")
        print(f"   Last update was {market_age:.1f} minutes ago")
        print("\n   To start the engine:")
        print("   python main.py")
else:
    print("❌ 15-MINUTE CYCLE: NOT STARTED")
    print("   No data in database yet")
    print("\n   To start the engine:")
    print("   python main.py")

print("="*70 + "\n")
