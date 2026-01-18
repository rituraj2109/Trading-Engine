import sqlite3
from config import Config
import json
from datetime import datetime

conn = sqlite3.connect(Config.DB_FILE)
c = conn.cursor()

# Create detailed report
report = []
report.append("="*80)
report.append("FOREX ENGINE - 15-MINUTE DATA SAVE VERIFICATION REPORT")
report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report.append("="*80)
report.append("")

# 1. Record Counts
c.execute('SELECT COUNT(*) FROM market_data')
market_count = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM signals')
signal_count = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM pattern_history')
pattern_count = c.fetchone()[0]

report.append("[1] TOTAL RECORDS SAVED")
report.append("-"*80)
report.append(f"Market Data Records: {market_count}")
report.append(f"Signal Records: {signal_count}")
report.append(f"Pattern Records: {pattern_count}")
report.append("")

# 2. Last update times
c.execute('SELECT MAX(time) FROM market_data')
last_market = c.fetchone()[0]
c.execute('SELECT MAX(time) FROM signals')
last_signal = c.fetchone()[0]

report.append("[2] LAST UPDATE TIMES")
report.append("-"*80)
report.append(f"Last Market Data: {last_market}")
report.append(f"Last Signal: {last_signal}")
report.append("")

# 3. Latest market data
report.append("[3] LATEST 5 MARKET DATA ENTRIES")
report.append("-"*80)
c.execute('SELECT time, pair, close, rsi, macd, atr FROM market_data ORDER BY time DESC LIMIT 5')
for row in c.fetchall():
    report.append(f"Time: {row[0]}")
    report.append(f"  Pair: {row[1]} | Price: {row[2]}")
    report.append(f"  RSI: {row[3]:.2f} | MACD: {row[4]:.5f} | ATR: {row[5]:.5f}")
    report.append("")

# 4. Latest signals
report.append("[4] LATEST 5 SIGNALS")
report.append("-"*80)
c.execute('SELECT time, pair, signal, confidence, entry_price, reason FROM signals ORDER BY time DESC LIMIT 5')
for row in c.fetchall():
    report.append(f"Time: {row[0]}")
    report.append(f"  Pair: {row[1]} | Signal: {row[2]} | Confidence: {row[3]}%")
    report.append(f"  Entry Price: {row[4]}")
    report.append(f"  Reason: {row[5]}")
    report.append("")

# 5. Latest patterns
report.append("[5] LATEST 5 CHART PATTERNS")
report.append("-"*80)
c.execute('SELECT time, pair, pattern_name, bias, score, confidence FROM pattern_history ORDER BY time DESC LIMIT 5')
rows = c.fetchall()
if rows:
    for row in rows:
        report.append(f"Time: {row[0]}")
        report.append(f"  Pair: {row[1]} | Pattern: {row[2]}")
        report.append(f"  Bias: {row[3]} | Score: {row[4]} | Confidence: {row[5]}")
        report.append("")
else:
    report.append("No patterns detected yet")
    report.append("")

# 6. Data by pair
report.append("[6] RECORDS BY TRADING PAIR")
report.append("-"*80)
c.execute('SELECT pair, COUNT(*) as count, MAX(time) as last_update FROM market_data GROUP BY pair ORDER BY count DESC')
for row in c.fetchall():
    report.append(f"{row[0]}: {row[1]} records | Last update: {row[2]}")
report.append("")

# 7. Signal distribution
report.append("[7] SIGNAL DISTRIBUTION")
report.append("-"*80)
c.execute('SELECT signal, COUNT(*) FROM signals GROUP BY signal')
for row in c.fetchall():
    report.append(f"{row[0]}: {row[1]} signals")
report.append("")

report.append("="*80)
report.append("END OF REPORT")
report.append("="*80)

# Save to file
output_text = "\n".join(report)
with open('DATA_VERIFICATION_REPORT.txt', 'w') as f:
    f.write(output_text)

# Also print to console
print(output_text)

conn.close()

print("\nReport saved to: DATA_VERIFICATION_REPORT.txt")
