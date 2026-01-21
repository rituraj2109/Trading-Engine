from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import pandas as pd
import threading
import os
import time
from config import Config
from main import background_job, run_analysis_cycle
from utils import init_db

app = Flask(__name__)

# Configure CORS to allow requests from Vercel frontend
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://trading-engine-frontend-yhhs.vercel.app",
            "https://trading-engine-frontend.vercel.app",
            "https://*.vercel.app",
            "http://localhost:5173",
            "http://localhost:5000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5000"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

# Add after_request handler for additional CORS headers
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept,Origin')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

def get_db_connection():
    conn = sqlite3.connect(Config.DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    """Root endpoint - API is running"""
    return jsonify({
        "message": "Trading Engine API is running",
        "version": "1.2",
        "endpoints": {
            "health": "/api/health",
            "status": "/api/status",
            "signals": "/api/signals",
            "news": "/api/news",
            "data": "/api/data/<pair>",
            "scan": "/api/scan (POST)"
        }
    })

@app.route('/api/health', methods=['GET'])
def health():
    """Simple health check endpoint"""
    return jsonify({"status": "ok", "timestamp": time.time()}), 200

@app.route('/api/status', methods=['GET'])
def status():
    # Check Mongo Status
    mongo_status = "disabled"
    mongo_uri_set = bool(Config.MONGO_URI and Config.MONGO_URI != "")
    
    if mongo_uri_set:
        try:
            from utils import get_mongo_db
            db = get_mongo_db()
            if db:
                db.command('ping')
                mongo_status = "connected"
            else:
                mongo_status = "not configured"
        except Exception as e:
            mongo_status = f"error: {str(e)[:100]}"
    
    return jsonify({
        "status": "running", 
        "version": "1.2",
        "database": "mongodb" if mongo_uri_set else "sqlite",
        "mongodb": mongo_status,
        "timestamp": time.time()
    })

@app.route('/api/signals', methods=['GET'])
def get_signals():
    try:
        from utils import get_mongo_db
        db = get_mongo_db()
        if db is None:
            return jsonify([])

        # Aggregation pipeline to get the latest signal per pair
        pipeline = [
            {"$sort": {"time": -1}},
            {"$group": {
                "_id": "$pair",
                "doc": {"$first": "$$ROOT"}
            }},
            {"$replaceRoot": {"newRoot": "$doc"}}
        ]
        
        signals = list(db.signals.aggregate(pipeline))
        
        # Convert _id and dates to string for JSON serialization
        for s in signals:
            s['_id'] = str(s['_id'])
            if 'created_at' in s: s['created_at'] = str(s['created_at'])
            
        return jsonify(signals)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/<pair>', methods=['GET'])
def get_market_data(pair):
    limit = int(request.args.get('limit', 50))
    try:
        from utils import get_mongo_db
        db = get_mongo_db()
        if db is None:
            return jsonify([])

        cursor = db.market_data.find({"pair": pair.upper()}).sort("time", -1).limit(limit)
        data = list(cursor)
        
        for d in data:
            d['_id'] = str(d['_id'])
            
        # Return sorted by time ascending for charts
        return jsonify(data[::-1])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/news', methods=['GET'])
def get_news():
    try:
        from utils import get_mongo_db
        db = get_mongo_db()
        if db is None:
            return jsonify([])

        cursor = db.news.find().sort("date", -1).limit(20)
        data = list(cursor)
        
        for d in data:
            d['_id'] = str(d['_id'])
            
        return jsonify(data)
    except Exception as e:
        print(f"News Mongo Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/scan', methods=['POST'])
def trigger_scan():
    """Manually trigger a full analysis cycle"""
    def run_async():
        print("Manual scan triggered via API...")
        run_analysis_cycle(mode="background")
        print("Manual scan completed.")
        
    t = threading.Thread(target=run_async, daemon=True)
    t.start()
    return jsonify({"status": "Scan started", "message": "Analysis running in background"}), 202

# Initialize background job when app starts (for Gunicorn)
def init_background_engine():
    """Initialize DB and start background engine thread"""
    init_db()
    t = threading.Thread(target=background_job, daemon=True)
    t.start()
    print("Background Engine Started...")

# Start background engine when module is imported by Gunicorn
init_background_engine()

# Combined Entry Point (for local development)
def start_app():
    # 1. Initialize DB
    init_db()
    
    # 2. Start Background Engine in a separate thread
    # This prevents the web server from blocking the data collection
    t = threading.Thread(target=background_job, daemon=True)
    t.start()
    print("Background Engine Started...")
    
    # 3. Start Web Server
    # Railway sets PORT env var
    port = int(os.environ.get("PORT", 5000))
    # Host must be 0.0.0.0 to be accessible publicly
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    start_app()
