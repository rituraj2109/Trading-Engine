Railway deployment notes
=======================

Overview
--------
This project runs as a long-lived worker (no web server). On Railway, declare a "Worker" service that runs the engine continuously.

Important caveat about storage
------------------------------
- Railway containers have ephemeral filesystem storage. The local SQLite file (`forex_engine.db` or whatever you set in `Config.DB_FILE`) will NOT be reliably persisted across redeploys. For production use, switch to a managed database (Postgres, MySQL) or an external persistent volume.

Files added for deployment
--------------------------
- `Dockerfile` — builds a container and runs `python main.py`.
- `Procfile` — declares a `worker: python main.py` process for platform convenience.
- `.dockerignore` — keeps dev files out of the image.
- `start.sh` — simple entrypoint wrapper (optional).
- `runtime.txt` — hints Python version for platforms that use it.

Environment variables (set in Railway project settings)
-----------------------------------------------------
Set your API keys and other configuration using Railway's Environment Variables UI. Example names used by this project (see `config.py`):

- `API_KEY_TWELVEDATA`
- `API_KEY_POLYGON`
- `API_KEY_ALPHAVANTAGE`
- `API_KEY_FINNHUB`
- `API_KEY_NEWSAPI`
- `API_KEY_FMP`
- `DB_FILE` (optional) — local path for SQLite (not recommended on Railway)

Deploy steps (quick)
--------------------
1. Push repo to GitHub.
2. In Railway, create a new project and connect the repository.
3. Choose Dockerfile deployment or let Railway build automatically.
4. In Railway, add the required environment variables (API keys).
5. If Railway asks for a start command, use `python main.py` (or `worker: python main.py` via Procfile).

Local Docker test
-----------------
Build and run locally to validate:
```bash
docker build -t trading-engine:local .
docker run --rm -e API_KEY_TWELVEDATA="$API_KEY_TWELVEDATA" trading-engine:local
```

Notes
-----
- Prefer an external DB for persistence; if you must use SQLite on Railway, consider backing up the DB to cloud storage regularly.
- Keep `.env` secret and do NOT commit it.
