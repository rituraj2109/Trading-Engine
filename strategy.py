from config import Config
from indicators import TechnicalAnalysis
from sentiment import SentimentEngine
from data_loader import DataLoader
from utils import logger, is_trading_hours, get_symbol_trading_hours, get_utc_to_ist
import pandas as pd
import os

class DecisionEngine:
    def __init__(self, use_ml=True):
        self.loader = DataLoader()
        self.ta = TechnicalAnalysis()
        self.sentiment = SentimentEngine()
        self.use_ml = use_ml
        self.ml_model = None
        
        # Try to load ML model if requested
        if self.use_ml:
            try:
                from ml_model import TradingMLModel
                self.ml_model = TradingMLModel(model_type='random_forest')
                
                # Try to load existing model
                if not self.ml_model.load_model():
                    logger.warning("ML model not found. Run ml_model.py to train first. Using rule-based system.")
                    self.ml_model = None
                else:
                    logger.info("ML model loaded successfully!")
            except Exception as e:
                logger.warning(f"Could not load ML model: {e}. Using rule-based system.")
                self.ml_model = None

    def analyze_pair(self, pair):
        """
        Main logic for a single pair.
        Returns dict with Signal details.
        """
        from datetime import datetime, timedelta
        
        # Validate symbol first
        if pair.upper() not in Config.VALID_SYMBOLS:
            dt_utc = datetime.utcnow()
            dt_ist = dt_utc + timedelta(hours=5, minutes=30)
            return {
                "time": dt_utc.isoformat(),
                "time_ist": dt_ist.strftime('%Y-%m-%d %H:%M:%S (IST)'),
                "pair": pair,
                "signal": "WAIT",
                "confidence": 0.0,
                "price": 0.0,
                "stop_loss": 0.0,
                "take_profit": 0.0,
                "reason": f"Invalid Symbol: '{pair}' not recognized",
                "scores": (0, 0)
            }
        
        # Helper to get current UTC ISO time
        def get_current_utc():
            return datetime.utcnow().isoformat()

        # Helper for empty return (Data Fetch Failed)
        def return_empty(reason):
             dt_utc = datetime.utcnow()
             dt_ist = dt_utc + timedelta(hours=5, minutes=30)
             return {
                "time": dt_utc.isoformat(),
                "pair": pair,
                "signal": "WAIT",
                "confidence": 0.0,
                "price": 0.0,
                "stop_loss": 0.0,
                "take_profit": 0.0,
                "reason": reason,
                "scores": (0, 0)
            }
        
        # 1. Fetch Data (Always, to support 24/7 logging/viewing)
        df = self.loader.fetch_market_data(pair)
        if df is None or len(df) < 50:
             return return_empty("Insufficient Data")
        
        # 2. Compute Technicals
        df = self.ta.add_indicators(df)
        latest_candle = df.iloc[-1]
        
        tech_score = self.ta.get_signal_score(latest_candle)
        
        # 3. Compute Sentiment
        sent_score = self.sentiment.get_pair_sentiment_score(pair)
        
        # 3.b Detect Chart Patterns (adds/subtracts score)
        patterns, pattern_score, pattern_details = self.ta.detect_chart_patterns(df, lookback=100)
        
        # 4. ML Prediction (if available)
        ml_signal = "HOLD"
        ml_confidence = 0.0
        ml_score = 0.0
        
        if self.ml_model is not None:
            try:
                # Prepare features for ML prediction
                features = latest_candle[self.ml_model.feature_columns].to_dict()
                ml_signal, ml_confidence = self.ml_model.predict_single(features)
                
                # Convert ML signal to score
                if ml_signal == 'BUY':
                    ml_score = 2.0 * ml_confidence  # Weight by confidence
                elif ml_signal == 'SELL':
                    ml_score = -2.0 * ml_confidence
                else:  # HOLD
                    ml_score = 0.0
                
                logger.info(f"ML Prediction for {pair}: {ml_signal} (confidence: {ml_confidence:.2f}, score: {ml_score:.2f})")
            except Exception as e:
                logger.warning(f"ML prediction failed: {e}")
                ml_score = 0.0
        
        # 5. Total Score (include pattern score and ML score)
        total_score = tech_score + sent_score + pattern_score + ml_score
        
        signal = "WAIT"
        if total_score >= Config.BUY_THRESHOLD:
            signal = "BUY"
        elif total_score <= Config.SELL_THRESHOLD:
            signal = "SELL"
            
        # 6. Risk Management Calculations
        atr = latest_candle['atr']
        price = latest_candle['close']
        
        sl = 0.0
        tp = 0.0
        
        if signal == "BUY":
            sl = price - (atr * Config.ATR_MULTIPLIER_SL)
            risk = price - sl
            tp = price + (risk * Config.MIN_RISK_REWARD)
        elif signal == "SELL":
            sl = price + (atr * Config.ATR_MULTIPLIER_SL)
            risk = sl - price
            tp = price - (risk * Config.MIN_RISK_REWARD)
            
        # 6. Check Symbol-Specific Trading Session
        session_info = get_symbol_trading_hours(pair)
        
        # Convert UTC time to IST for display
        dt_utc = pd.to_datetime(latest_candle['datetime'])
        dt_ist = dt_utc + pd.Timedelta(hours=5, minutes=30)
        
        if "JPY" in pair:
            precision = 3
        elif "XAU" in pair or "XAG" in pair:
            precision = 2
        else:
            precision = 5
            
        final_reason = f"Tech: {tech_score:.1f}, Sentiment: {sent_score:.1f}"
        if ml_score != 0.0:
            final_reason += f", ML: {ml_signal} ({ml_confidence:.0%})"
        if patterns:
            final_reason += f", Patterns: {', '.join(patterns[:3])}"  # Limit to first 3 patterns
        
        # Override signal if market is closed (but still store data)
        if not session_info['is_open']:
            signal = "WAIT"
            final_reason = f"Market Closed - {session_info['session_name']}"
            if ml_score != 0.0:
                final_reason += f" | ML: {ml_signal}"
            if patterns:
                final_reason += f" | Patterns: {', '.join(patterns[:2])}"
            
        return {
            "time": dt_utc.isoformat(),  # Store UTC ISO-8601
            "time_ist": dt_ist.strftime('%Y-%m-%d %H:%M:%S (IST)'),  # Display IST
            "pair": pair,
            "signal": signal,
            "confidence": round(abs(total_score)/5.0 * 100, 2), 
            "price": round(price, precision),
            "stop_loss": round(sl, precision),
            "take_profit": round(tp, precision),
            "reason": final_reason,
            "scores": (tech_score, sent_score, ml_score if self.ml_model else 0),
            "ml_prediction": {
                "signal": ml_signal,
                "confidence": ml_confidence
            } if self.ml_model else None,
            "session_info": session_info,
            "raw_data": {
                "time": dt_utc.isoformat(), # Store as UTC ISO string
                "open": latest_candle['open'],
                "high": latest_candle['high'],
                "low": latest_candle['low'],
                "close": latest_candle['close'],
                "rsi": latest_candle.get('rsi', 0),
                "macd": latest_candle.get('macd', 0),
                "atr": latest_candle.get('atr', 0),
                "ema_20": latest_candle.get('ema_20', 0),
                "ema_50": latest_candle.get('ema_50', 0)
            },
            "patterns": patterns,
            "pattern_score": pattern_score,
            "pattern_details": pattern_details
        }
