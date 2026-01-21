# Trading-Engine

Forex AI Decision Engine — signal generator and data collector

> Live Backend: https://trading-engine-production-b04c.up.railway.app

What this project is
--------------------
This is a lightweight decision engine that collects market data, computes technical indicators and chart patterns, processes news sentiment, and produces BUY / SELL / WAIT signals on a configurable set of symbols.

Purpose
-------
- Provide structured, timestamped market + indicator history for analysis.
- Produce trade signals (with stop-loss, take-profit and confidence) to assist manual trading or further research.
- Store all market, signal and news history in a local SQLite database for auditing, backtesting and accuracy tracking.

Key features
------------
- Scheduled background fetch: runs every 15 minutes and saves OHLC candles + indicators.
- Technical indicators: RSI, MACD, ATR, EMA20, EMA50 (extendable).
- Chart pattern detection and scoring stored in `pattern_history`.
- News fetching and sentiment scoring from multiple providers.
- Signal generation combining technicals + sentiment + patterns with risk management (SL/TP computed using ATR).
- Accuracy tracking utilities to evaluate signals over time.

How it works (short)
--------------------
1. `main.py` initializes the DB and runs an initial analysis pass.
2. A background scheduler runs `run_analysis_cycle` every 15 minutes:
	- Fetches market data for configured `PAIRS`.
	- Calculates indicators and patterns.
	- Updates news & sentiment.
	- Generates and saves signals to the database.
3. An interactive prompt allows on-demand analysis of any valid symbol.

Storage & configuration
-----------------------
- Database: SQLite file configured by `Config.DB_FILE` (defaults to `forex_engine.db`).
- API keys: set in a `.env` file (not committed) or environment variables. Keys are loaded by `python-dotenv`.
- Files intentionally excluded from GitHub: `.env`, the SQLite DB, logs and test/monitor scripts (see `.gitignore`).

Quick start
-----------
1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Add API keys to a `.env` file (see `config.py` for required keys).
3. Run the engine:
```bash
python main.py
```
4. While running, type symbols at the prompt to get on-demand analysis, or leave it running to collect data every 15 minutes.

Useful commands
---------------
- Check 15-min cycle status: `python check_15min_cycle.py`
- Export DB tables to text: `python export_db_to_txt.py` (creates `exports/`)
- Run accuracy analysis (after 24+ hours of data): `python accuracy_tracker.py` (local only; not pushed)

Notes & safety
--------------
- This project generates signals only. It does NOT place orders or connect to brokers.
- Keep your `.env` private — it contains API keys.
- Let the engine run for 24–48 hours to collect meaningful accuracy statistics.

Contributing / extensions
-------------------------
- Add more symbols to `Config.VALID_SYMBOLS` and `Config.PAIRS`.
- Add more indicator modules in `indicators.py`.
- Swap or add news/data providers in `data_loader.py`.

License & contact
-----------------
This is a personal project — adapt as needed. For questions, open an issue in the GitHub repository.

