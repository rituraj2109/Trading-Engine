"""
Check DB status: counts and latest timestamps for market_data, signals, news, pattern_history
"""
import sqlite3
from datetime import datetime, timezone
import pandas as pd

from config import Config
DB = Config.DB_FILE

def q(sql, params=()):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows

print('\nDB:', DB)

# Counts
market_count = q('SELECT COUNT(*) FROM market_data')[0][0]
signal_count = q('SELECT COUNT(*) FROM signals')[0][0]
news_count = q('SELECT COUNT(*) FROM news')[0][0]
pattern_count = q('SELECT COUNT(*) FROM pattern_history')[0][0]

print(f'Counts -> market_data: {market_count}, signals: {signal_count}, news: {news_count}, pattern_history: {pattern_count}')

# Latest times per table
def latest_market_per_pair(limit=10):
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query('SELECT * FROM market_data', conn)
    conn.close()
    if df.empty:
        return None, None
    # Parse ISO-8601 UTC timestamps
    df['time_parsed'] = pd.to_datetime(df['time'], utc=True, format='ISO8601', errors='coerce')
    latest_overall = df['time_parsed'].max()
    latest_per_pair = df.groupby('pair')['time_parsed'].max().reset_index().sort_values('time_parsed', ascending=False)
    return latest_overall, latest_per_pair.head(limit)

latest_market_overall, latest_market_pairs = latest_market_per_pair(limit=20)
if latest_market_overall is not None:
    now_utc = datetime.now(timezone.utc)
    delta = now_utc - latest_market_overall.to_pydatetime().replace(tzinfo=timezone.utc)
    print(f'Latest market_data overall: {latest_market_overall} UTC (age: {delta.total_seconds()/60:.1f} minutes)')
    print('\nLatest market_data per pair:')
    print(latest_market_pairs.to_string(index=False))
else:
    print('No market_data found')

# Latest signals per pair
conn = sqlite3.connect(DB)
sig_df = pd.read_sql_query('SELECT * FROM signals', conn)
conn.close()
if not sig_df.empty:
    sig_df['time_parsed'] = pd.to_datetime(sig_df['time'], utc=True, format='ISO8601', errors='coerce')
    latest_sig_overall = sig_df['time_parsed'].max()
    now_utc = datetime.now(timezone.utc)
    delta_sig = now_utc - latest_sig_overall.to_pydatetime().replace(tzinfo=timezone.utc)
    print(f'\nLatest signals overall: {latest_sig_overall} UTC (age: {delta_sig.total_seconds()/60:.1f} minutes)')
    latest_sig_pairs = sig_df.groupby('pair')['time_parsed'].max().reset_index().sort_values('time_parsed', ascending=False)
    print('\nLatest signals per pair:')
    print(latest_sig_pairs.head(20).to_string(index=False))
else:
    print('\nNo signals found')

# Latest news
rows = q('SELECT MAX(date) FROM news')
if rows and rows[0][0]:
    try:
        latest_news = pd.to_datetime(rows[0][0])
        now_utc = datetime.now(timezone.utc)
        delta_news = now_utc - latest_news.to_pydatetime().replace(tzinfo=timezone.utc)
        print(f'\nLatest news date: {latest_news} (age: {delta_news.total_seconds()/3600:.1f} hours)')
    except Exception:
        print('\nLatest news date (raw):', rows[0][0])
else:
    print('\nNo news found')

# Recommend
print('\nRecommendation:')
if latest_market_overall is not None and (datetime.now(timezone.utc) - latest_market_overall.to_pydatetime().replace(tzinfo=timezone.utc)).total_seconds() <= 60*20:
    print('  • Market data updated within last 20 minutes → 15-min cycle appears active')
else:
    print('  • Market data is older than 20 minutes → 15-min cycle may not be running or API calls paused')

if not sig_df.empty and (datetime.now(timezone.utc) - latest_sig_overall.to_pydatetime().replace(tzinfo=timezone.utc)).total_seconds() <= 60*20:
    print('  • Signals updated within last 20 minutes')
else:
    print('  • Signals not updated recently')

if news_count > 0:
    print('  • News present in DB')
else:
    print('  • No news present')

print('\nCheck completed')
