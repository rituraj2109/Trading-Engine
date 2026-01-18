"""
Quick API Test Script - Diagnose API Issues
"""
import requests
from config import Config
from datetime import datetime, timedelta

def test_polygon():
    """Test Polygon API"""
    print("\n=== TESTING POLYGON API ===")
    if Config.API_KEY_POLYGON == "DEMO_KEY":
        print("❌ Polygon API key is set to DEMO_KEY")
        return
    
    print(f"✓ API Key: {Config.API_KEY_POLYGON[:10]}...")
    
    symbol = "GBPUSD"
    ticker = f"C:{symbol}"
    end = datetime.utcnow().strftime('%Y-%m-%d')
    start = (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    url = f"{Config.URL_POLYGON}/v2/aggs/ticker/{ticker}/range/15/minute/{start}/{end}"
    params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": 100,
        "apiKey": Config.API_KEY_POLYGON
    }
    
    print(f"URL: {url}")
    print(f"Ticker: {ticker}")
    print(f"Date Range: {start} to {end}")
    
    try:
        resp = requests.get(url, params=params)
        print(f"Status Code: {resp.status_code}")
        data = resp.json()
        print(f"Response: {data}")
        
        if data.get('status') == 'ERROR':
            print(f"❌ ERROR: {data.get('error', data.get('message', 'Unknown'))}")
        elif data.get('resultsCount', 0) > 0:
            print(f"✓ Success! Got {data['resultsCount']} results")
        else:
            print(f"⚠ No results. Status: {data.get('status')}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_twelvedata():
    """Test TwelveData API"""
    print("\n=== TESTING TWELVEDATA API ===")
    if Config.API_KEY_TWELVEDATA == "DEMO_KEY":
        print("❌ TwelveData API key is set to DEMO_KEY")
        return
    
    print(f"✓ API Key: {Config.API_KEY_TWELVEDATA[:10]}...")
    
    symbol = "GBP/USD"
    url = f"{Config.URL_TWELVEDATA}/time_series"
    params = {
        "symbol": symbol,
        "interval": "15min",
        "outputsize": 10,
        "apikey": Config.API_KEY_TWELVEDATA
    }
    
    print(f"URL: {url}")
    print(f"Symbol: {symbol}")
    
    try:
        resp = requests.get(url, params=params)
        print(f"Status Code: {resp.status_code}")
        data = resp.json()
        
        if 'values' in data:
            print(f"✓ Success! Got {len(data['values'])} values")
            print(f"Latest: {data['values'][0]}")
        else:
            print(f"❌ Error: {data}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_alphavantage():
    """Test AlphaVantage API"""
    print("\n=== TESTING ALPHAVANTAGE API ===")
    if Config.API_KEY_ALPHAVANTAGE == "DEMO_KEY":
        print("❌ AlphaVantage API key is set to DEMO_KEY")
        return
    
    print(f"✓ API Key: {Config.API_KEY_ALPHAVANTAGE[:10]}...")
    
    url = f"{Config.URL_ALPHAVANTAGE}?function=FX_INTRADAY&from_symbol=GBP&to_symbol=USD&interval=15min&apikey={Config.API_KEY_ALPHAVANTAGE}"
    
    print(f"URL: {url[:100]}...")
    
    try:
        resp = requests.get(url)
        print(f"Status Code: {resp.status_code}")
        data = resp.json()
        
        if "Time Series FX (15min)" in data:
            print(f"✓ Success! Got data")
        elif "Note" in data:
            print(f"⚠ Rate Limit: {data['Note']}")
        elif "Error Message" in data:
            print(f"❌ Error: {data['Error Message']}")
        else:
            print(f"Response Keys: {list(data.keys())}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("API Testing Script")
    print("=" * 50)
    
    test_polygon()
    test_twelvedata()
    test_alphavantage()
    
    print("\n" + "=" * 50)
    print("Testing Complete!")
