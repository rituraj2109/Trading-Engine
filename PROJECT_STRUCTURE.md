# Trading Engine - Python Backend Structure

## 📁 Project Overview
This is a Python backend for a Forex Trading Engine with AI-powered decision making.

## 🗂️ Core Application Files

### Main Application
- **`main.py`** - Entry point for the trading engine
- **`config.py`** - Configuration settings and API keys

### Data & Analysis Modules
- **`data_loader.py`** - Fetches market data from multiple APIs
- **`indicators.py`** - Technical indicators calculations (RSI, MACD, Bollinger Bands, etc.)
- **`sentiment.py`** - News sentiment analysis
- **`strategy.py`** - Trading strategy and decision logic
- **`utils.py`** - Utility functions and helpers
- **`accuracy_tracker.py`** - Tracks and analyzes prediction accuracy
- **`generate_report.py`** - Generates analytical reports

## 🚀 Deployment Files

### Docker Deployment
- **`Dockerfile`** - Docker container configuration
- **`.dockerignore`** - Files to exclude from Docker image

### Platform Deployment
- **`Procfile`** - Process file for Railway/Heroku deployment
- **`requirements.txt`** - Python dependencies
- **`runtime.txt`** - Python runtime version
- **`start.sh`** - Shell script to start the application
- **`vps_setup.sh`** - VPS server setup script

## 📋 Configuration Files
- **`.env`** - Environment variables (API keys, secrets) - **NOT in git**
- **`.gitignore`** - Files to exclude from git repository
- **`README.md`** - Project documentation

## 📊 Data Storage (Runtime Generated)
- **`forex_engine.db`** - SQLite database (auto-created at runtime)
- **`trading_engine.log`** - Application logs (auto-created)
- **`exports/`** - Exported reports and data dumps

## 🔧 Dependencies
See `requirements.txt` for all Python package dependencies.

## 🎯 How to Deploy

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Docker Deployment
```bash
# Build the image
docker build -t trading-engine .

# Run the container
docker run -p 8000:8000 --env-file .env trading-engine
```

### Railway/Cloud Deployment
1. Connect your GitHub repository
2. Railway will auto-detect the Procfile
3. Set environment variables from .env
4. Deploy automatically

## 📝 Notes
- Database and logs are created automatically at runtime
- All test files have been removed for production deployment
- Ensure `.env` file is configured with all required API keys
- The application runs 24/7, collecting data and generating signals during trading hours
