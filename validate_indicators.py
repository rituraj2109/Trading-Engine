"""Simple Indicator Validation - Text Output Only"""

import pandas as pd
import numpy as np
from datetime import datetime

def validate():
    print("="*60)
    print("INDICATOR VALIDATION CHECK")
    print("="*60)
    
    # Import check
    try:
        from indicators import TechnicalAnalysis
        print("[OK] TechnicalAnalysis imported")
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        return
    
    # Create test data
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=200, freq='15min')
    close = 1.1000 + np.cumsum(np.random.randn(200) * 0.0005)
    high = close + np.abs(np.random.randn(200) * 0.0003)
    low = close - np.abs(np.random.randn(200) * 0.0003)
    
    df = pd.DataFrame({
        'time': dates,
        'open': close + np.random.randn(200) * 0.0002,
        'high': high,
        'low': low,
        'close': close,
        'volume': np.random.randint(1000, 10000, 200)
    })
    
    print(f"[OK] Test data: {len(df)} rows")
    
    # Add indicators
    try:
        df = TechnicalAnalysis.add_indicators(df)
        print("[OK] Indicators calculated")
    except Exception as e:
        print(f"[ERROR] Calculation failed: {e}")
        return
    
    # Check 5 core indicators
    print("\n" + "="*60)
    print("CORE INDICATORS (Required)")
    print("="*60)
    
    indicators = [
        ("1. EMA", ['ema_20', 'ema_50']),
        ("2. RSI", ['rsi']),
        ("3. MACD", ['macd', 'macd_signal', 'macd_diff']),
        ("4. ATR", ['atr']),
        ("5. Stochastic", ['stoch_k', 'stoch_d'])
    ]
    
    all_ok = True
    for name, cols in indicators:
        present = all(col in df.columns for col in cols)
        has_data = all(df[col].notna().sum() > 0 for col in cols) if present else False
        
        if present and has_data:
            print(f"[OK] {name}: {', '.join(cols)}")
        else:
            print(f"[FAIL] {name}: Missing or no data")
            all_ok = False
    
    # Test signal
    print("\n" + "="*60)
    print("SIGNAL GENERATION TEST")
    print("="*60)
    
    try:
        last = df.iloc[-1]
        score = TechnicalAnalysis.get_signal_score(last)
        print(f"[OK] Score: {score:.2f}")
        print(f"     EMA20: {last['ema_20']:.5f}")
        print(f"     RSI: {last['rsi']:.2f}")
        print(f"     MACD: {last['macd']:.5f}")
    except Exception as e:
        print(f"[ERROR] Signal failed: {e}")
    
    # Test patterns
    print("\n" + "="*60)
    print("PATTERN DETECTION TEST")
    print("="*60)
    
    try:
        patterns, score, details = TechnicalAnalysis.detect_chart_patterns(df)
        print(f"[OK] {len(patterns)} patterns detected")
        print(f"     Score: {score:.2f}")
        if patterns:
            for p in patterns[:3]:
                print(f"     - {p}")
    except Exception as e:
        print(f"[ERROR] Pattern detection failed: {e}")
    
    print("\n" + "="*60)
    print("RESULT")
    print("="*60)
    if all_ok:
        print("ALL 5 INDICATORS WORKING!")
    else:
        print("SOME INDICATORS FAILED!")
    print("="*60)

if __name__ == "__main__":
    validate()
