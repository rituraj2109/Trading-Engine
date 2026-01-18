"""Quick test to verify signal saving after datetime fixes"""
from strategy import DecisionEngine
from utils import get_db_connection
import pandas as pd

print("Testing signal generation and DB save...")

engine = DecisionEngine()
conn = get_db_connection()

# Test with EURUSD
print("\n1. Analyzing EURUSD...")
result = engine.analyze_pair("EURUSD")

print(f"   Signal: {result['signal']}")
print(f"   Time (UTC ISO): {result['time']}")
print(f"   Time (IST): {result.get('time_ist', 'N/A')}")

# Save signal
print("\n2. Saving signal to database...")
cursor = conn.cursor()
cursor.execute('''
    INSERT INTO signals (time, pair, signal, confidence, entry_price, stop_loss, take_profit, reason)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (result['time'], 'EURUSD', result['signal'], result['confidence'], 
      result['price'], result['stop_loss'], result['take_profit'], result['reason']))
conn.commit()
print("   ✓ Signal saved")

# Verify
print("\n3. Verifying from database...")
sig_df = pd.read_sql_query("SELECT * FROM signals WHERE pair='EURUSD' ORDER BY time DESC LIMIT 1", conn)
print(sig_df[['time', 'pair', 'signal', 'confidence']])

# Parse datetime
sig_df['time_parsed'] = pd.to_datetime(sig_df['time'], utc=True, format='ISO8601', errors='coerce')
print(f"\n   Parsed time: {sig_df['time_parsed'].iloc[0]}")
print(f"   Is valid: {not pd.isna(sig_df['time_parsed'].iloc[0])}")

conn.close()
print("\n✓ Test complete")
