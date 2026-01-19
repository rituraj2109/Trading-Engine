from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import pandas as pd
import threading
import os
from config import Config
from main import background_job, run_analysis_cycle
from utils import init_db

app = Flask(__name__, static_folder='frontend/dist')
CORS(app) # Enable CORS for frontend access

def get_db_connection():
    conn = sqlite3.connect(Config.DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return app.send_static_file(path)
    else:
        return app.send_static_file('index.html')

@app.route('/api/status', methods=['GET'])
def status():
    # Check Mongo Status
    mongo_status = "disabled"
    if Config.MONGO_URI:
        try:
            from utils import get_mongo_db
            db = get_mongo_db()
            db.command('ping')
            mongo_status = "connected"
        except Exception as e:
            mongo_status = f"error: {str(e)}"
            
    return jsonify({
        "status": "running", 
        "version": "1.2",
        "database": "sqlite",
        "mongodb": mongo_status
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

# Combined Entry Point
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
