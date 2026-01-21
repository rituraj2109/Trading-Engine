# Phase 1 Quick Reference Card

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Collect data (run for 24-48 hours)
python main.py

# 3. Train ML model
python train_ml_model.py --optimize

# 4. Validate everything works
python validate_phase1.py

# 5. Run with ML enabled
python main.py
```

## 📊 What Changed

### New Indicators (3)
1. **Stochastic Oscillator** - Overbought/oversold detection
2. **Bollinger Bands** - Volatility and price extremes
3. **On-Balance Volume** - Volume-based confirmation

### ML Features (21 total)
- All original indicators + 12 engineered features
- Price changes, volatility, momentum
- Percentage-based normalization

### Models Available
- **Random Forest** (default) - Robust, fast
- **Gradient Boosting** - Often more accurate
- **XGBoost** - High performance (optional)

## 🎯 Key Commands

```bash
# Train with optimization (2-3 hours)
python train_ml_model.py --optimize

# Quick train (5-10 minutes)
python train_ml_model.py --no-optimize

# Train specific pairs only
python train_ml_model.py --pairs EURUSD,GBPUSD

# Run validation tests
python validate_phase1.py

# Disable ML temporarily
# Edit strategy.py: engine = DecisionEngine(use_ml=False)
```

## 🔧 Configuration (config.py)

```python
USE_ML_MODEL = True              # Enable/disable ML
ML_MODEL_TYPE = 'random_forest'  # Model to use
ML_CONFIDENCE_THRESHOLD = 0.6    # Min confidence
BUY_THRESHOLD = 3.5              # Signal threshold
SELL_THRESHOLD = -3.5            # Signal threshold
```

## 📈 Signal Scoring

```
Total = Technical + Sentiment + Pattern + ML

Technical (-10 to +10):
  EMA trends:        ±1.5
  RSI:               ±1.5
  MACD:              ±1.0
  Stochastic:        ±1.0
  Bollinger Bands:   ±1.0
  OBV:               ±0.5

ML Score (-2 to +2):
  Confidence-weighted prediction
```

## 🎓 Target Metrics

- **Accuracy**: 60%+
- **Cross-validation**: 5 folds
- **Min data**: 24-48 hours collection
- **Features**: 21 engineered
- **Classes**: BUY, HOLD, SELL

## 📁 New Files

| File | Purpose |
|------|---------|
| `ml_model.py` | ML implementation |
| `train_ml_model.py` | Training script |
| `validate_phase1.py` | Test suite |
| `PHASE1_IMPLEMENTATION.md` | Full docs |
| `PHASE1_SUMMARY.md` | Completion summary |
| `PHASE1_QUICKREF.md` | This file |

## 🔍 Troubleshooting

### Model not loading?
```bash
# Check if model file exists
ls exports/ml_model_*.pkl

# Retrain if missing
python train_ml_model.py
```

### Low accuracy?
1. Collect more data (48+ hours)
2. Try different thresholds
3. Use --optimize flag
4. Check feature importance

### Tests failing?
```bash
# Re-run validation
python validate_phase1.py

# Check for errors
python -c "from strategy import DecisionEngine; print('OK')"
```

## 💡 Best Practices

1. ✅ Collect data before training
2. ✅ Use --optimize for production
3. ✅ Validate before deploying
4. ✅ Monitor performance
5. ✅ Retrain periodically

## 📊 Expected Output

### Training Output:
```
Training random_forest model with 2000 samples...
Best parameters: {'max_depth': 20, 'n_estimators': 200, ...}
Best CV score: 0.6234

Cross-validation Results:
Accuracy:  0.6234 (+/- 0.0321)
Precision: 0.6189 (+/- 0.0298)

Test Set Evaluation:
Accuracy:  0.6312
```

### Prediction Output:
```
ML Prediction for EURUSD: BUY (confidence: 0.73, score: 1.46)
Signal: BUY
Confidence: 68%
Reason: Tech: 2.5, Sentiment: 0.8, ML: BUY (73%), Patterns: Ascending Triangle
```

## 🎯 Phase 1 Checklist

- [x] Enhanced existing indicators
- [x] Added 3 new indicators
- [x] Improved feature engineering
- [x] Implemented ML models
- [x] Added cross-validation
- [x] Hyperparameter tuning
- [x] Integration with strategy
- [x] Complete documentation
- [x] Validation suite
- [x] All tests passing

## 🏆 Status: COMPLETE ✅

Phase 1 successfully implemented and validated!

## 📖 More Info

- **Full Documentation**: PHASE1_IMPLEMENTATION.md
- **Completion Report**: PHASE1_SUMMARY.md
- **Project Plan**: PLAN.md

---

**Need Help?** Run `python validate_phase1.py` to verify your setup.
