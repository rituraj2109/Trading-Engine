"""
Export all SQLite tables to text files (TSV) in ./exports/
Also creates a combined summary file exports/db_dump.txt
"""
import os
import sqlite3
import pandas as pd
from config import Config

DB = Config.DB_FILE or 'forex_engine.db'
OUT_DIR = os.path.join(os.path.dirname(__file__), 'exports')
os.makedirs(OUT_DIR, exist_ok=True)

def list_tables(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    return [r[0] for r in cur.fetchall()]

def export_table(conn, table, out_dir):
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    out_path = os.path.join(out_dir, f"{table}.txt")
    df.to_csv(out_path, sep='\t', index=False)
    return out_path, len(df)

def main():
    print(f"Using DB: {DB}")
    conn = sqlite3.connect(DB)
    tables = list_tables(conn)
    print(f"Found tables: {tables}")

    summary_lines = []
    for t in tables:
        path, rows = export_table(conn, t, OUT_DIR)
        summary_lines.append(f"{t}: {rows} rows -> {path}")
        print(f"Exported {t} -> {path} ({rows} rows)")

    # Combined dump
    combined_path = os.path.join(OUT_DIR, 'db_dump.txt')
    with open(combined_path, 'w', encoding='utf-8') as fh:
        fh.write(f"Database dump for {DB}\n")
        fh.write("=\n")
        for t in tables:
            fh.write(f"\nTABLE: {t}\n")
            fh.write('-' * 80 + '\n')
            df = pd.read_sql_query(f"SELECT * FROM {t} LIMIT 1000", conn)
            fh.write(df.to_csv(sep='\t', index=False))
            fh.write('\n')

    conn.close()
    print('\nSummary:')
    for line in summary_lines:
        print(line)
    print(f"Combined dump: {combined_path}")
    print('Done.')

if __name__ == "__main__":
    main()
