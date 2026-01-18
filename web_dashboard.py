from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import pandas as pd
import threading
import os
from config import Config
from main import background_job
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
    conn = get_db_connection()
    # Get latest signal for each pair
    query = '''
        SELECT s.* 
        FROM signals s
        INNER JOIN (
            SELECT pair, MAX(time) as max_time
            FROM signals
            GROUP BY pair
        ) latest ON s.pair = latest.pair AND s.time = latest.max_time
    '''
    try:
        signals = conn.execute(query).fetchall()
        result = [dict(row) for row in signals]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/data/<pair>', methods=['GET'])
def get_market_data(pair):
    conn = get_db_connection()
    limit = request.args.get('limit', 50)
    try:
        query = f'''
            SELECT * FROM market_data 
            WHERE pair = ? 
            ORDER BY time DESC 
            LIMIT ?
        '''
        data = conn.execute(query, (pair.upper(), limit)).fetchall()
        result = [dict(row) for row in data]
        # Return sorted by time ascending for charts
        return jsonify(result[::-1])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/news', methods=['GET'])
def get_news():
    conn = get_db_connection()
    try:
        query = 'SELECT * FROM news ORDER BY date DESC LIMIT 20'
        data = conn.execute(query).fetchall()
        result = [dict(row) for row in data]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

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
