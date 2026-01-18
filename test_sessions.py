"""
Test Symbol-Specific Trading Sessions
"""
from utils import get_symbol_trading_hours, get_utc_to_ist
from datetime import datetime

def test_sessions():
    print("\n" + "="*60)
    print("TRADING SESSION STATUS TEST")
    print("="*60)
    
    current_ist = get_utc_to_ist()
    print(f"\nCurrent Time (IST): {current_ist.strftime('%Y-%m-%d %H:%M:%S %A')}")
    print(f"Current Time (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "-"*60)
    
    symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]
    
    for symbol in symbols:
        print(f"\n{symbol}:")
        info = get_symbol_trading_hours(symbol)
        
        if info['is_open']:
            print(f"  Status: ✅ OPEN")
            print(f"  Session: {info['session_name']}")
        else:
            print(f"  Status: ❌ CLOSED")
            print(f"  Reason: {info['session_name']}")
            if info['next_open_ist']:
                print(f"  Next Open: {info['next_open_ist']}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_sessions()
