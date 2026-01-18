"""
db_status_console.py
Prints database connection status and basic table counts to the console.
"""
import os
import sqlite3
from config import Config

# Determine DB path (fallback to forex_engine.db if not set)
db_path = Config.DB_FILE or os.getenv('DB_FILE') or 'forex_engine.db'
print(f"Database file: {db_path}")

# File exists?
exists = os.path.exists(db_path)
print(f"Exists: {exists}")
if exists:
    size = os.path.getsize(db_path)
    print(f"Size: {size} bytes")

# Try to connect
try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    print("Connection: OK")

    # List tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    print(f"Tables ({len(tables)}): {', '.join(tables)}")

    # Check counts for common tables
    for t in ['market_data', 'signals', 'news', 'pattern_history']:
        if t in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {t}")
                cnt = cur.fetchone()[0]
                print(f"  {t}: {cnt} rows")
            except Exception as e:
                print(f"  {t}: error reading count: {e}")
        else:
            print(f"  {t}: NOT FOUND")

    conn.close()
except Exception as e:
    print(f"Connection: FAILED -> {e}")

print("\nDone.")
