import sqlite3

conn = sqlite3.connect('forex_engine.db')
c = conn.cursor()

print("\n" + "="*60)
print("RECENT DATA SAVED - QUICK CHECK")
print("="*60)

# Count records
c.execute('SELECT COUNT(*) FROM market_data')
market_count = c.fetchone()[0]

c.execute('SELECT COUNT(*) FROM signals')
signal_count = c.fetchone()[0]

c.execute('SELECT COUNT(*) FROM pattern_history')
pattern_count = c.fetchone()[0]

print(f"\nTotal Records Saved:")
print(f"  Market Data: {market_count}")
print(f"  Signals: {signal_count}")
print(f"  Patterns: {pattern_count}")

# Last update times
c.execute('SELECT MAX(time) FROM market_data')
last_market = c.fetchone()[0]

c.execute('SELECT MAX(time) FROM signals')
last_signal = c.fetchone()[0]

print(f"\nLast Update Times:")
print(f"  Market Data: {last_market}")
print(f"  Signals: {last_signal}")

# Latest 3 market data entries
print(f"\nLast 3 Market Data Entries:")
print("-"*60)
c.execute('SELECT time, pair, close, rsi FROM market_data ORDER BY time DESC LIMIT 3')
for row in c.fetchall():
    print(f"{row[0]} | {row[1]} | Price: {row[2]} | RSI: {row[3]:.1f}")

# Latest 3 signals
print(f"\nLast 3 Signals:")
print("-"*60)
c.execute('SELECT time, pair, signal, confidence FROM signals ORDER BY time DESC LIMIT 3')
for row in c.fetchall():
    print(f"{row[0]} | {row[1]} | {row[2]} | Conf: {row[3]}")

# Data by pair
print(f"\nRecords by Pair:")
print("-"*60)
c.execute('SELECT pair, COUNT(*) FROM market_data GROUP BY pair ORDER BY COUNT(*) DESC')
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]} records")

conn.close()
print("\n" + "="*60)
