"""
Phase 1 Validation Script
=========================
Tests all Phase 1 enhancements to ensure they work correctly.
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_indicators():
    """Test new technical indicators"""
    print("=" * 60)
    print("Testing Enhanced Indicators")
    print("=" * 60)
    
    try:
        from indicators import TechnicalAnalysis
        
        # Create sample OHLCV data
        dates = pd.date_range(end=datetime.now(), periods=200, freq='15min')
        np.random.seed(42)
        
        close_prices = 100 + np.cumsum(np.random.randn(200) * 0.5)
        df = pd.DataFrame({
            'datetime': dates,
            'open': close_prices + np.random.randn(200) * 0.2,
            'high': close_prices + np.abs(np.random.randn(200)) * 0.5,
            'low': close_prices - np.abs(np.random.randn(200)) * 0.5,
            'close': close_prices,
            'volume': np.random.randint(1000, 10000, 200)
        })
        
        # Add indicators
        ta = TechnicalAnalysis()
        df = ta.add_indicators(df)
        
        # Check new indicators exist
        new_indicators = ['stoch_k', 'stoch_d', 'bb_upper', 'bb_lower', 'bb_width', 
                         'bb_pct', 'obv', 'obv_ema', 'price_change', 'volatility', 
                         'momentum', 'rsi_ema', 'atr_pct', 'high_low_pct']
        
        missing = [ind for ind in new_indicators if ind not in df.columns]
        
        if missing:
            print(f"❌ Missing indicators: {missing}")
            return False
        
        print("✅ All new indicators added successfully")
        
        # Test scoring
        latest = df.iloc[-1]
        score = ta.get_signal_score(latest)
        print(f"✅ Signal scoring works (score: {score:.2f})")
        
        # Test pattern detection
        patterns, pattern_score, pattern_details = ta.detect_chart_patterns(df)
        print(f"✅ Pattern detection works (found {len(patterns)} patterns)")
        
        return True
        
    except Exception as e:
        print(f"❌ Indicator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ml_model():
    """Test ML model implementation"""
    print("\n" + "=" * 60)
    print("Testing ML Model")
    print("=" * 60)
    
    try:
        from ml_model import TradingMLModel
        from indicators import TechnicalAnalysis
        
        # Create sample data with indicators
        dates = pd.date_range(end=datetime.now(), periods=300, freq='15min')
        np.random.seed(42)
        
        close_prices = 100 + np.cumsum(np.random.randn(300) * 0.5)
        df = pd.DataFrame({
            'datetime': dates,
            'open': close_prices + np.random.randn(300) * 0.2,
            'high': close_prices + np.abs(np.random.randn(300)) * 0.5,
            'low': close_prices - np.abs(np.random.randn(300)) * 0.5,
            'close': close_prices,
            'volume': np.random.randint(1000, 10000, 300)
        })
        
        # Add indicators
        ta = TechnicalAnalysis()
        df = ta.add_indicators(df)
        
        # Initialize model
        model = TradingMLModel(model_type='random_forest')
        print("✅ ML model initialized")
        
        # Prepare features
        X, y = model.prepare_features(df)
        
        if X is None or y is None:
            print("❌ Feature preparation failed")
            return False
        
        print(f"✅ Feature preparation successful ({len(X)} samples, {len(X.columns)} features)")
        print(f"   Features: {', '.join(X.columns[:5])}...")
        print(f"   Class distribution: {y.value_counts().to_dict()}")
        
        # Test model training (quick, no optimization)
        if len(X) > 100:
            print("\n   Training model (quick test, no optimization)...")
            model.train_model(X[:200], y[:200], optimize_hyperparameters=False)
            print("✅ Model training successful")
            
            # Test prediction
            X_test = X.iloc[-10:]
            predictions, probabilities = model.predict(X_test)
            print(f"✅ Model prediction works (predictions: {predictions[:3]})")
            
            # Test single prediction
            features_dict = X.iloc[-1].to_dict()
            signal, confidence = model.predict_single(features_dict)
            print(f"✅ Single prediction works: {signal} (confidence: {confidence:.2%})")
        else:
            print("⚠️  Not enough data for training test, but structure is valid")
        
        return True
        
    except Exception as e:
        print(f"❌ ML model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_strategy_integration():
    """Test ML integration in strategy"""
    print("\n" + "=" * 60)
    print("Testing Strategy Integration")
    print("=" * 60)
    
    try:
        from strategy import DecisionEngine
        
        # Test initialization with ML disabled (won't fail if model not trained)
        engine = DecisionEngine(use_ml=False)
        print("✅ Strategy engine initialized (ML disabled)")
        
        # Test with ML enabled (will warn if model not found, but won't crash)
        engine_ml = DecisionEngine(use_ml=True)
        print("✅ Strategy engine initialized (ML enabled)")
        
        if engine_ml.ml_model is not None:
            print("✅ ML model loaded successfully in strategy")
        else:
            print("⚠️  ML model not loaded (needs training first)")
        
        return True
        
    except Exception as e:
        print(f"❌ Strategy integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """Test configuration updates"""
    print("\n" + "=" * 60)
    print("Testing Configuration")
    print("=" * 60)
    
    try:
        from config import Config
        
        # Check new config options exist
        assert hasattr(Config, 'USE_ML_MODEL'), "USE_ML_MODEL not in config"
        assert hasattr(Config, 'ML_MODEL_TYPE'), "ML_MODEL_TYPE not in config"
        assert hasattr(Config, 'ML_CONFIDENCE_THRESHOLD'), "ML_CONFIDENCE_THRESHOLD not in config"
        
        print("✅ All new config options present")
        print(f"   USE_ML_MODEL: {Config.USE_ML_MODEL}")
        print(f"   ML_MODEL_TYPE: {Config.ML_MODEL_TYPE}")
        print(f"   ML_CONFIDENCE_THRESHOLD: {Config.ML_CONFIDENCE_THRESHOLD}")
        print(f"   BUY_THRESHOLD: {Config.BUY_THRESHOLD}")
        print(f"   SELL_THRESHOLD: {Config.SELL_THRESHOLD}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation tests"""
    print("\n" + "=" * 60)
    print("PHASE 1 VALIDATION SUITE")
    print("=" * 60)
    print("Testing all Phase 1 enhancements...\n")
    
    results = {
        "Indicators": test_indicators(),
        "ML Model": test_ml_model(),
        "Strategy Integration": test_strategy_integration(),
        "Configuration": test_config()
    }
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Phase 1 Implementation Verified!")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Collect data: Run main.py for 24-48 hours")
        print("3. Train model: python train_ml_model.py --optimize")
        print("4. Run with ML: python main.py (auto-loads trained model)")
    else:
        print("❌ SOME TESTS FAILED - Please review errors above")
        print("=" * 60)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
