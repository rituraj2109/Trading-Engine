"""
Training Script for ML Models
==============================
Run this script to train ML models on historical data.

Usage:
    python train_ml_model.py [--optimize] [--pairs EURUSD,GBPUSD]
"""

import argparse
import sys
from ml_model import train_models_from_historical_data
from utils import logger

def main():
    parser = argparse.ArgumentParser(description='Train ML models for trading signals')
    parser.add_argument('--optimize', action='store_true', 
                        help='Perform hyperparameter optimization (slower but better results)')
    parser.add_argument('--pairs', type=str, default=None,
                        help='Comma-separated list of pairs to train on (default: all)')
    parser.add_argument('--no-optimize', dest='optimize', action='store_false',
                        help='Skip hyperparameter optimization (faster training)')
    parser.set_defaults(optimize=True)
    
    args = parser.parse_args()
    
    pairs = None
    if args.pairs:
        pairs = [p.strip() for p in args.pairs.split(',')]
    
    logger.info("="*60)
    logger.info("ML Model Training Script")
    logger.info("="*60)
    logger.info(f"Hyperparameter Optimization: {'Enabled' if args.optimize else 'Disabled'}")
    if pairs:
        logger.info(f"Training on pairs: {', '.join(pairs)}")
    else:
        logger.info("Training on all available pairs")
    logger.info("="*60)
    
    try:
        best_model, best_accuracy = train_models_from_historical_data(
            pairs=pairs, 
            optimize=args.optimize
        )
        
        logger.info("\n" + "="*60)
        logger.info("Training Completed Successfully!")
        logger.info(f"Best Model: {best_model}")
        logger.info(f"Best Accuracy: {best_accuracy:.2%}")
        logger.info("="*60)
        
        if best_accuracy < 0.60:
            logger.warning("\nWARNING: Accuracy below 60% target!")
            logger.info("Suggestions:")
            logger.info("1. Collect more historical data (run bot longer)")
            logger.info("2. Try different time periods")
            logger.info("3. Adjust feature engineering")
            logger.info("4. Consider ensemble methods")
        else:
            logger.info("\n✓ Target accuracy of 60% achieved!")
            logger.info("Model is ready for use in trading strategy.")
        
        return 0
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
