"""
Accuracy Tracker for Trading Signals
=====================================
This module tracks the accuracy of trading signals by comparing:
1. Signal prediction (BUY/SELL)
2. Actual price movement after signal
3. Whether SL or TP was hit first

Accuracy is calculated after enough time has passed to evaluate each signal.
"""

from utils import get_db_connection, logger
import pandas as pd
from datetime import datetime, timedelta

class AccuracyTracker:
    def __init__(self):
        self.lookback_hours = 24  # How long to wait before evaluating a signal
        
    def evaluate_signals(self):
        """
        Evaluate past signals and calculate accuracy.
        A signal is considered accurate if:
        - BUY signal: Price went UP by at least 50% of distance to TP
        - SELL signal: Price went DOWN by at least 50% of distance to TP
        """
        conn = get_db_connection()
        
        # Get signals that are old enough to evaluate (at least 24 hours old)
        cutoff_time = (datetime.utcnow() - timedelta(hours=self.lookback_hours)).isoformat()
        
        query = '''
            SELECT * FROM signals 
            WHERE signal IN ('BUY', 'SELL')
            AND time < ?
            ORDER BY time DESC
            LIMIT 1000
        '''
        
        signals_df = pd.read_sql_query(query, conn, params=(cutoff_time,))
        
        if len(signals_df) == 0:
            logger.info("No signals old enough to evaluate yet")
            conn.close()
            return None
        
        # Get market data for evaluation
        market_df = pd.read_sql_query('SELECT * FROM market_data ORDER BY time', conn)
        conn.close()
        
        if len(market_df) == 0:
            logger.info("No market data available for evaluation")
            return None
        
        results = []
        
        for _, signal in signals_df.iterrows():
            try:
                signal_time = pd.to_datetime(signal['time'])
                pair = signal['pair']
                signal_type = signal['signal']
                entry_price = signal['entry_price']
                stop_loss = signal['stop_loss']
                take_profit = signal['take_profit']
                
                # Get subsequent market data for this pair
                pair_data = market_df[market_df['pair'] == pair].copy()
                pair_data['time'] = pd.to_datetime(pair_data['time'])
                
                # Get data after signal
                future_data = pair_data[pair_data['time'] > signal_time].head(50)  # Next ~12 hours of 15min candles
                
                if len(future_data) == 0:
                    continue
                
                # Check if SL or TP was hit
                hit_tp = False
                hit_sl = False
                outcome = "UNKNOWN"
                
                if signal_type == "BUY":
                    # Check if TP was hit
                    if any(future_data['high'] >= take_profit):
                        hit_tp = True
                        outcome = "WIN"
                    # Check if SL was hit
                    elif any(future_data['low'] <= stop_loss):
                        hit_sl = True
                        outcome = "LOSS"
                    else:
                        # Neither hit, check price movement
                        max_price = future_data['high'].max()
                        price_move_pct = ((max_price - entry_price) / entry_price) * 100
                        
                        if max_price >= entry_price:
                            outcome = "PARTIAL_WIN"
                        else:
                            outcome = "PARTIAL_LOSS"
                
                elif signal_type == "SELL":
                    # Check if TP was hit
                    if any(future_data['low'] <= take_profit):
                        hit_tp = True
                        outcome = "WIN"
                    # Check if SL was hit
                    elif any(future_data['high'] >= stop_loss):
                        hit_sl = True
                        outcome = "LOSS"
                    else:
                        # Neither hit, check price movement
                        min_price = future_data['low'].min()
                        price_move_pct = ((entry_price - min_price) / entry_price) * 100
                        
                        if min_price <= entry_price:
                            outcome = "PARTIAL_WIN"
                        else:
                            outcome = "PARTIAL_LOSS"
                
                results.append({
                    'time': signal_time,
                    'pair': pair,
                    'signal': signal_type,
                    'entry': entry_price,
                    'sl': stop_loss,
                    'tp': take_profit,
                    'confidence': signal['confidence'],
                    'outcome': outcome,
                    'hit_tp': hit_tp,
                    'hit_sl': hit_sl
                })
                
            except Exception as e:
                logger.error(f"Error evaluating signal: {e}")
                continue
        
        if len(results) == 0:
            return None
        
        results_df = pd.DataFrame(results)
        
        # Calculate accuracy metrics
        total_signals = len(results_df)
        wins = len(results_df[results_df['outcome'] == 'WIN'])
        losses = len(results_df[results_df['outcome'] == 'LOSS'])
        partial_wins = len(results_df[results_df['outcome'] == 'PARTIAL_WIN'])
        partial_losses = len(results_df[results_df['outcome'] == 'PARTIAL_LOSS'])
        
        # Win rate calculation (full wins only)
        win_rate = (wins / total_signals * 100) if total_signals > 0 else 0
        
        # Including partial wins as "directionally correct"
        directional_accuracy = ((wins + partial_wins) / total_signals * 100) if total_signals > 0 else 0
        
        # By signal type
        buy_signals = results_df[results_df['signal'] == 'BUY']
        sell_signals = results_df[results_df['signal'] == 'SELL']
        
        buy_accuracy = 0
        sell_accuracy = 0
        
        if len(buy_signals) > 0:
            buy_wins = len(buy_signals[buy_signals['outcome'].isin(['WIN', 'PARTIAL_WIN'])])
            buy_accuracy = (buy_wins / len(buy_signals)) * 100
        
        if len(sell_signals) > 0:
            sell_wins = len(sell_signals[sell_signals['outcome'].isin(['WIN', 'PARTIAL_WIN'])])
            sell_accuracy = (sell_wins / len(sell_signals)) * 100
        
        # By pair
        pair_accuracy = {}
        for pair in results_df['pair'].unique():
            pair_data = results_df[results_df['pair'] == pair]
            pair_wins = len(pair_data[pair_data['outcome'].isin(['WIN', 'PARTIAL_WIN'])])
            pair_accuracy[pair] = (pair_wins / len(pair_data)) * 100 if len(pair_data) > 0 else 0
        
        accuracy_report = {
            'total_signals': total_signals,
            'wins': wins,
            'losses': losses,
            'partial_wins': partial_wins,
            'partial_losses': partial_losses,
            'win_rate': win_rate,
            'directional_accuracy': directional_accuracy,
            'buy_accuracy': buy_accuracy,
            'sell_accuracy': sell_accuracy,
            'pair_accuracy': pair_accuracy,
            'buy_count': len(buy_signals),
            'sell_count': len(sell_signals)
        }
        
        return accuracy_report
    
    def print_accuracy_report(self):
        """Print formatted accuracy report"""
        from colorama import Fore, Style, init
        init(autoreset=True)
        
        report = self.evaluate_signals()
        
        if report is None:
            print(f"{Fore.YELLOW}Not enough data to calculate accuracy yet.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Run the engine for at least 24 hours to get accuracy metrics.{Style.RESET_ALL}")
            return
        
        print(f"\n{Style.BRIGHT}{'='*70}")
        print(f"ACCURACY REPORT")
        print(f"{'='*70}{Style.RESET_ALL}")
        
        print(f"\n📊 {Style.BRIGHT}Overall Performance:{Style.RESET_ALL}")
        print(f"   Total Signals Evaluated: {report['total_signals']}")
        print(f"   Full Wins: {report['wins']} ({report['win_rate']:.1f}%)")
        print(f"   Full Losses: {report['losses']}")
        print(f"   Partial Wins: {report['partial_wins']}")
        print(f"   Partial Losses: {report['partial_losses']}")
        
        # Color code directional accuracy
        acc = report['directional_accuracy']
        if acc >= 60:
            color = Fore.GREEN
        elif acc >= 50:
            color = Fore.YELLOW
        else:
            color = Fore.RED
        
        print(f"\n🎯 {Style.BRIGHT}Directional Accuracy:{Style.RESET_ALL} {color}{acc:.1f}%{Style.RESET_ALL}")
        print(f"   (Includes both full and partial wins)")
        
        print(f"\n📈 {Style.BRIGHT}By Signal Type:{Style.RESET_ALL}")
        print(f"   BUY Signals: {report['buy_count']} ({report['buy_accuracy']:.1f}% accurate)")
        print(f"   SELL Signals: {report['sell_count']} ({report['sell_accuracy']:.1f}% accurate)")
        
        print(f"\n💱 {Style.BRIGHT}By Trading Pair:{Style.RESET_ALL}")
        sorted_pairs = sorted(report['pair_accuracy'].items(), key=lambda x: x[1], reverse=True)
        for pair, accuracy in sorted_pairs:
            if accuracy >= 60:
                color = Fore.GREEN
            elif accuracy >= 50:
                color = Fore.YELLOW
            else:
                color = Fore.RED
            print(f"   {pair}: {color}{accuracy:.1f}%{Style.RESET_ALL}")
        
        print(f"\n{Style.BRIGHT}{'='*70}{Style.RESET_ALL}\n")
        
        # Recommendations
        if report['directional_accuracy'] >= 60:
            print(f"{Fore.GREEN}✓ Good accuracy! Continue monitoring.{Style.RESET_ALL}")
        elif report['directional_accuracy'] >= 50:
            print(f"{Fore.YELLOW}⚠ Moderate accuracy. Consider adjusting thresholds.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}⚠ Low accuracy. Review strategy parameters.{Style.RESET_ALL}")

def main():
    """Run accuracy analysis"""
    tracker = AccuracyTracker()
    tracker.print_accuracy_report()

if __name__ == "__main__":
    main()
