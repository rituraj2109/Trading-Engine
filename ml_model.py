"""
Machine Learning Model for Trading Signal Prediction
====================================================
This module implements ML-based trading signal prediction with:
- Feature engineering from technical indicators
- Multiple ML models (Random Forest, XGBoost, Gradient Boosting)
- Cross-validation and hyperparameter tuning
- Model persistence and retraining
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, TimeSeriesSplit, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import joblib
import os
from datetime import datetime
from utils import logger, get_mongo_db
from data_loader import DataLoader
from indicators import TechnicalAnalysis

class TradingMLModel:
    def __init__(self, model_type='random_forest'):
        """
        Initialize ML Model
        
        Args:
            model_type: 'random_forest', 'gradient_boosting', or 'xgboost'
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.model_path = f'exports/ml_model_{model_type}.pkl'
        self.scaler_path = f'exports/ml_scaler_{model_type}.pkl'
        
        # Create exports directory if it doesn't exist
        os.makedirs('exports', exist_ok=True)
        
    def prepare_features(self, df):
        """
        Prepare features from dataframe with technical indicators
        
        Args:
            df: DataFrame with OHLCV data and technical indicators
            
        Returns:
            X: Feature matrix
            y: Target labels (1=BUY, 0=HOLD, -1=SELL)
        """
        # Ensure all indicators are present
        if 'rsi' not in df.columns:
            return None, None
        
        # Define features to use
        feature_list = [
            'rsi', 'rsi_ema', 'macd', 'macd_signal', 'macd_diff',
            'atr', 'atr_pct', 'ema_20', 'ema_50',
            'stoch_k', 'stoch_d', 
            'bb_upper', 'bb_lower', 'bb_width', 'bb_pct',
            'price_change', 'volatility', 'momentum', 'high_low_pct'
        ]
        
        # Add OBV if volume data available
        if 'obv' in df.columns and df['obv'].sum() != 0:
            feature_list.extend(['obv', 'obv_ema'])
        
        # Filter features that exist in df
        available_features = [f for f in feature_list if f in df.columns]
        self.feature_columns = available_features
        
        X = df[available_features].copy()
        
        # Generate target labels based on future price movement
        # Look ahead N periods to determine if price went up/down/sideways
        lookback_periods = 4  # 1 hour (4 x 15min candles)
        df['future_return'] = df['close'].shift(-lookback_periods) / df['close'] - 1
        
        # Define thresholds for BUY/SELL signals
        buy_threshold = 0.003   # 0.3% gain
        sell_threshold = -0.003  # 0.3% loss
        
        # Create labels: 1=BUY, 0=HOLD, -1=SELL (but we'll treat as multiclass: 0, 1, 2)
        y = pd.Series(index=df.index, dtype=int)
        y[df['future_return'] > buy_threshold] = 2  # BUY
        y[(df['future_return'] >= sell_threshold) & (df['future_return'] <= buy_threshold)] = 1  # HOLD
        y[df['future_return'] < sell_threshold] = 0  # SELL
        
        # Remove rows with NaN (from shift and indicator calculations)
        valid_idx = ~(X.isna().any(axis=1) | y.isna())
        X = X[valid_idx]
        y = y[valid_idx]
        
        return X, y
    
    def train_model(self, X, y, optimize_hyperparameters=True):
        """
        Train the ML model with cross-validation
        
        Args:
            X: Feature matrix
            y: Target labels
            optimize_hyperparameters: Whether to perform hyperparameter tuning
        """
        logger.info(f"Training {self.model_type} model with {len(X)} samples...")
        
        # Use TimeSeriesSplit for cross-validation (respects temporal order)
        tscv = TimeSeriesSplit(n_splits=5)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        if self.model_type == 'random_forest':
            if optimize_hyperparameters:
                logger.info("Optimizing hyperparameters for Random Forest...")
                param_grid = {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [10, 20, 30, None],
                    'min_samples_split': [2, 5, 10],
                    'min_samples_leaf': [1, 2, 4],
                    'max_features': ['sqrt', 'log2']
                }
                
                base_model = RandomForestClassifier(random_state=42, n_jobs=-1)
                grid_search = GridSearchCV(
                    base_model, param_grid, cv=tscv, 
                    scoring='accuracy', n_jobs=-1, verbose=1
                )
                grid_search.fit(X_scaled, y)
                self.model = grid_search.best_estimator_
                logger.info(f"Best parameters: {grid_search.best_params_}")
                logger.info(f"Best CV score: {grid_search.best_score_:.4f}")
            else:
                self.model = RandomForestClassifier(
                    n_estimators=200, 
                    max_depth=20,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    max_features='sqrt',
                    random_state=42,
                    n_jobs=-1
                )
                self.model.fit(X_scaled, y)
                
        elif self.model_type == 'gradient_boosting':
            if optimize_hyperparameters:
                logger.info("Optimizing hyperparameters for Gradient Boosting...")
                param_grid = {
                    'n_estimators': [100, 200, 300],
                    'learning_rate': [0.01, 0.05, 0.1],
                    'max_depth': [3, 5, 7],
                    'min_samples_split': [2, 5, 10],
                    'subsample': [0.8, 0.9, 1.0]
                }
                
                base_model = GradientBoostingClassifier(random_state=42)
                grid_search = GridSearchCV(
                    base_model, param_grid, cv=tscv,
                    scoring='accuracy', n_jobs=-1, verbose=1
                )
                grid_search.fit(X_scaled, y)
                self.model = grid_search.best_estimator_
                logger.info(f"Best parameters: {grid_search.best_params_}")
                logger.info(f"Best CV score: {grid_search.best_score_:.4f}")
            else:
                self.model = GradientBoostingClassifier(
                    n_estimators=200,
                    learning_rate=0.05,
                    max_depth=5,
                    min_samples_split=5,
                    subsample=0.9,
                    random_state=42
                )
                self.model.fit(X_scaled, y)
        
        # Try importing XGBoost if available
        elif self.model_type == 'xgboost':
            try:
                import xgboost as xgb
                if optimize_hyperparameters:
                    logger.info("Optimizing hyperparameters for XGBoost...")
                    param_grid = {
                        'n_estimators': [100, 200, 300],
                        'learning_rate': [0.01, 0.05, 0.1],
                        'max_depth': [3, 5, 7],
                        'min_child_weight': [1, 3, 5],
                        'subsample': [0.8, 0.9, 1.0],
                        'colsample_bytree': [0.8, 0.9, 1.0]
                    }
                    
                    base_model = xgb.XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='mlogloss')
                    grid_search = GridSearchCV(
                        base_model, param_grid, cv=tscv,
                        scoring='accuracy', n_jobs=-1, verbose=1
                    )
                    grid_search.fit(X_scaled, y)
                    self.model = grid_search.best_estimator_
                    logger.info(f"Best parameters: {grid_search.best_params_}")
                    logger.info(f"Best CV score: {grid_search.best_score_:.4f}")
                else:
                    self.model = xgb.XGBClassifier(
                        n_estimators=200,
                        learning_rate=0.05,
                        max_depth=5,
                        min_child_weight=3,
                        subsample=0.9,
                        colsample_bytree=0.9,
                        random_state=42,
                        use_label_encoder=False,
                        eval_metric='mlogloss'
                    )
                    self.model.fit(X_scaled, y)
            except ImportError:
                logger.warning("XGBoost not available, falling back to Random Forest")
                self.model_type = 'random_forest'
                self.train_model(X, y, optimize_hyperparameters=False)
                return
        
        logger.info(f"Model training completed!")
        
    def cross_validate(self, X, y):
        """
        Perform time-series cross-validation and report metrics
        
        Args:
            X: Feature matrix
            y: Target labels
            
        Returns:
            dict: Cross-validation scores
        """
        logger.info("Performing time-series cross-validation...")
        
        tscv = TimeSeriesSplit(n_splits=5)
        X_scaled = self.scaler.transform(X)
        
        cv_scores = {
            'accuracy': [],
            'precision': [],
            'recall': [],
            'f1': []
        }
        
        for fold, (train_idx, val_idx) in enumerate(tscv.split(X_scaled)):
            X_train, X_val = X_scaled[train_idx], X_scaled[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            self.model.fit(X_train, y_train)
            y_pred = self.model.predict(X_val)
            
            cv_scores['accuracy'].append(accuracy_score(y_val, y_pred))
            cv_scores['precision'].append(precision_score(y_val, y_pred, average='weighted', zero_division=0))
            cv_scores['recall'].append(recall_score(y_val, y_pred, average='weighted', zero_division=0))
            cv_scores['f1'].append(f1_score(y_val, y_pred, average='weighted', zero_division=0))
            
            logger.info(f"Fold {fold+1}: Accuracy={cv_scores['accuracy'][-1]:.4f}")
        
        # Calculate mean and std
        results = {}
        for metric, scores in cv_scores.items():
            results[f'{metric}_mean'] = np.mean(scores)
            results[f'{metric}_std'] = np.std(scores)
            logger.info(f"{metric.capitalize()}: {results[f'{metric}_mean']:.4f} (+/- {results[f'{metric}_std']:.4f})")
        
        return results
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate model on test set
        
        Args:
            X_test: Test features
            y_test: Test labels
            
        Returns:
            dict: Evaluation metrics
        """
        X_test_scaled = self.scaler.transform(X_test)
        y_pred = self.model.predict(X_test_scaled)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        logger.info(f"\n{'='*50}")
        logger.info(f"Model Evaluation Results ({self.model_type})")
        logger.info(f"{'='*50}")
        logger.info(f"Accuracy:  {accuracy:.4f}")
        logger.info(f"Precision: {precision:.4f}")
        logger.info(f"Recall:    {recall:.4f}")
        logger.info(f"F1-Score:  {f1:.4f}")
        logger.info(f"\nClassification Report:")
        logger.info(classification_report(y_test, y_pred, target_names=['SELL', 'HOLD', 'BUY']))
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
    
    def predict(self, X):
        """
        Make predictions
        
        Args:
            X: Feature matrix
            
        Returns:
            predictions: Array of predictions (0=SELL, 1=HOLD, 2=BUY)
            probabilities: Probability estimates for each class
        """
        if self.model is None:
            logger.error("Model not trained or loaded!")
            return None, None
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        return predictions, probabilities
    
    def predict_single(self, features_dict):
        """
        Make prediction for a single data point
        
        Args:
            features_dict: Dictionary of feature values
            
        Returns:
            signal: 'BUY', 'HOLD', or 'SELL'
            confidence: Probability of the prediction
        """
        # Create DataFrame with single row
        X = pd.DataFrame([features_dict])[self.feature_columns]
        
        predictions, probabilities = self.predict(X)
        
        if predictions is None:
            return 'HOLD', 0.0
        
        pred = int(predictions[0])  # Convert to int
        confidence = float(probabilities[0][pred])  # Convert to float
        
        signal_map = {0: 'SELL', 1: 'HOLD', 2: 'BUY'}
        signal = signal_map[pred]
        
        return signal, confidence
    
    def get_feature_importance(self, top_n=15):
        """
        Get feature importance scores
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            DataFrame with feature names and importance scores
        """
        if self.model is None:
            logger.error("Model not trained!")
            return None
        
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            feature_importance = pd.DataFrame({
                'feature': self.feature_columns,
                'importance': importances
            }).sort_values('importance', ascending=False)
            
            logger.info(f"\nTop {top_n} Most Important Features:")
            logger.info(feature_importance.head(top_n).to_string(index=False))
            
            return feature_importance.head(top_n)
        else:
            logger.warning("Model does not support feature importance")
            return None
    
    def save_model(self):
        """Save trained model and scaler to disk"""
        if self.model is None:
            logger.error("No model to save!")
            return False
        
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            joblib.dump(self.feature_columns, f'exports/feature_columns_{self.model_type}.pkl')
            logger.info(f"Model saved to {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
    
    def load_model(self):
        """Load trained model and scaler from disk"""
        if not os.path.exists(self.model_path):
            logger.warning(f"Model file not found: {self.model_path}")
            return False
        
        try:
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            self.feature_columns = joblib.load(f'exports/feature_columns_{self.model_type}.pkl')
            logger.info(f"Model loaded from {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False


def train_models_from_historical_data(pairs=None, optimize=True):
    """
    Train ML models using historical data from MongoDB
    
    Args:
        pairs: List of trading pairs to use (None = use all available)
        optimize: Whether to optimize hyperparameters
    """
    logger.info("="*60)
    logger.info("Starting ML Model Training Pipeline")
    logger.info("="*60)
    
    # Get data from MongoDB
    db = get_mongo_db()
    if db is None:
        logger.error("MongoDB connection failed!")
        return
    
    # Fetch historical market data
    market_data = list(db.market_data.find())
    
    if len(market_data) == 0:
        logger.error("No historical data available in MongoDB!")
        logger.info("Please run the bot for a while to collect data first.")
        return
    
    df = pd.DataFrame(market_data)
    logger.info(f"Loaded {len(df)} historical data points")
    
    if pairs:
        df = df[df['pair'].isin(pairs)]
        logger.info(f"Filtered to {len(df)} data points for pairs: {pairs}")
    
    # Convert time to datetime
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time')
    
    # Train separate models or combined - here we'll train combined
    # Remove MongoDB _id field
    if '_id' in df.columns:
        df = df.drop('_id', axis=1)
    
    # Prepare features for all data
    ta = TechnicalAnalysis()
    all_X = []
    all_y = []
    
    # Process each pair separately to maintain time series integrity
    for pair in df['pair'].unique():
        pair_df = df[df['pair'] == pair].copy()
        
        # Need OHLCV to recalculate indicators properly
        required_cols = ['open', 'high', 'low', 'close']
        if not all(col in pair_df.columns for col in required_cols):
            logger.warning(f"Pair {pair} missing required OHLCV columns, skipping...")
            continue
        
        # Add volume if missing (use dummy values for forex)
        if 'volume' not in pair_df.columns:
            pair_df['volume'] = 1000  # Dummy volume for forex pairs
            logger.info(f"Added dummy volume for {pair}")
        
        # Add datetime if missing
        if 'datetime' not in pair_df.columns:
            pair_df['datetime'] = pair_df['time']
        
        # Recalculate indicators to ensure all features are present
        try:
            pair_df = ta.add_indicators(pair_df)
            logger.info(f"Recalculated indicators for {pair}: {len(pair_df)} rows")
        except Exception as e:
            logger.warning(f"Failed to add indicators for {pair}: {e}")
            continue
        
        # Prepare features
        model = TradingMLModel()
        X, y = model.prepare_features(pair_df)
        
        if X is not None and len(X) > 20:  # Reduced threshold from 50
            all_X.append(X)
            all_y.append(y)
            logger.info(f"Prepared {len(X)} samples for {pair}")
        else:
            logger.warning(f"Insufficient samples for {pair}: {len(X) if X is not None else 0}")
    
    if len(all_X) == 0:
        logger.error("No valid data for training!")
        logger.info("Troubleshooting tips:")
        logger.info("1. Ensure main.py has run for at least a few hours to collect data")
        logger.info("2. Check MongoDB connection is working")
        logger.info("3. Verify market_data collection has OHLC data")
        return None, 0.0
    
    # Combine all data
    X_combined = pd.concat(all_X, ignore_index=True)
    y_combined = pd.concat(all_y, ignore_index=True)
    
    logger.info(f"Total training samples: {len(X_combined)}")
    
    if len(X_combined) < 100:
        logger.warning(f"⚠️  Only {len(X_combined)} samples available. Recommended: 500+")
        logger.warning("Model may not be very accurate with limited data.")
        logger.info("Consider running main.py longer to collect more data.")
    
    logger.info(f"Class distribution:")
    logger.info(y_combined.value_counts())
    
    # Split data (80-20 train-test, but respecting time series)
    # If data is very limited, use 70-30 to ensure enough training data
    if len(X_combined) < 200:
        split_idx = int(len(X_combined) * 0.7)
        logger.info("Using 70-30 split due to limited data")
    else:
        split_idx = int(len(X_combined) * 0.8)
        
    X_train, X_test = X_combined[:split_idx], X_combined[split_idx:]
    y_train, y_test = y_combined[:split_idx], y_combined[split_idx:]
    
    logger.info(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")
    
    # Train multiple models
    models_to_train = ['random_forest', 'gradient_boosting']
    
    best_model = None
    best_accuracy = 0
    
    for model_type in models_to_train:
        logger.info(f"\n{'='*60}")
        logger.info(f"Training {model_type.upper()} model")
        logger.info(f"{'='*60}")
        
        model = TradingMLModel(model_type=model_type)
        model.train_model(X_train, y_train, optimize_hyperparameters=optimize)
        
        # Cross-validate
        cv_results = model.cross_validate(X_train, y_train)
        
        # Evaluate on test set
        test_results = model.evaluate(X_test, y_test)
        
        # Feature importance
        model.get_feature_importance()
        
        # Save model
        model.save_model()
        
        # Track best model
        if test_results['accuracy'] > best_accuracy:
            best_accuracy = test_results['accuracy']
            best_model = model_type
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Training Complete!")
    logger.info(f"Best Model: {best_model} (Accuracy: {best_accuracy:.4f})")
    logger.info(f"{'='*60}")
    
    return best_model, best_accuracy


if __name__ == "__main__":
    # Train models when run directly
    train_models_from_historical_data(optimize=True)
