#!/usr/bin/env python3
"""
Display all saved data from the forex_engine database
"""

import sqlite3
from config import Config
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

def show_database_contents():
    """Display all tables and their recent data"""
    
    conn = sqlite3.connect(Config.DB_FILE)
    cursor = conn.cursor()
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"📊 FOREX ENGINE DATABASE - SAVED DATA")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    # 1. Market Data Table
    print(f"{Fore.YELLOW}{'─'*80}")
    print(f"📈 MARKET DATA TABLE")
    print(f"{'─'*80}{Style.RESET_ALL}")
    
    cursor.execute("SELECT COUNT(*) FROM market_data")
    count = cursor.fetchone()[0]
    print(f"Total Records: {Fore.GREEN}{count}{Style.RESET_ALL}\n")
    
    if count > 0:
        cursor.execute("""
            SELECT time, pair, open, high, low, close, rsi, macd, atr
            FROM market_data 
            ORDER BY time DESC 
            LIMIT 15
        """)
        
        print(f"{'Time':<20} {'Pair':<10} {'Open':<10} {'High':<10} {'Low':<10} {'Close':<10} {'RSI':<8} {'MACD':<8}")
        print("─" * 95)
        
        for row in cursor.fetchall():
            time, pair, open_p, high, low, close, rsi, macd, atr = row
            print(f"{time:<20} {pair:<10} {open_p:<10.5f} {high:<10.5f} {low:<10.5f} {close:<10.5f} {rsi:<8.2f} {macd:<8.4f}")
    
    # 2. Signals Table
    print(f"\n{Fore.YELLOW}{'─'*80}")
    print(f"🎯 SIGNALS TABLE")
    print(f"{'─'*80}{Style.RESET_ALL}")
    
    cursor.execute("SELECT COUNT(*) FROM signals")
    count = cursor.fetchone()[0]
    print(f"Total Records: {Fore.GREEN}{count}{Style.RESET_ALL}\n")
    
    if count > 0:
        cursor.execute("""
            SELECT time, pair, signal, confidence, entry_price, stop_loss, take_profit
            FROM signals 
            ORDER BY time DESC 
            LIMIT 15
        """)
        
        print(f"{'Time':<20} {'Pair':<10} {'Signal':<8} {'Conf%':<8} {'Entry':<10} {'SL':<10} {'TP':<10}")
        print("─" * 85)
        
        for row in cursor.fetchall():
            time, pair, signal, confidence, entry, sl, tp = row
            
            if signal == "BUY":
                signal_color = Fore.GREEN
            elif signal == "SELL":
                signal_color = Fore.RED
            else:
                signal_color = Fore.YELLOW
            
            print(f"{time:<20} {pair:<10} {signal_color}{signal:<8}{Style.RESET_ALL} {confidence:<8.2f} {entry:<10.5f} {sl:<10.5f} {tp:<10.5f}")
    
    # 3. Pattern History Table
    print(f"\n{Fore.YELLOW}{'─'*80}")
    print(f"📐 PATTERN HISTORY TABLE")
    print(f"{'─'*80}{Style.RESET_ALL}")
    
    cursor.execute("SELECT COUNT(*) FROM pattern_history")
    count = cursor.fetchone()[0]
    print(f"Total Records: {Fore.GREEN}{count}{Style.RESET_ALL}\n")
    
    if count > 0:
        cursor.execute("""
            SELECT time, pair, pattern_name, bias, score, confidence
            FROM pattern_history 
            ORDER BY time DESC 
            LIMIT 20
        """)
        
        print(f"{'Time':<20} {'Pair':<10} {'Pattern':<40} {'Bias':<10} {'Score':<8} {'Conf%':<8}")
        print("─" * 100)
        
        for row in cursor.fetchall():
            time, pair, pattern_name, bias, score, confidence = row
            
            if 'Bullish' in bias:
                bias_color = Fore.GREEN
                icon = "▲"
            elif 'Bearish' in bias:
                bias_color = Fore.RED
                icon = "▼"
            else:
                bias_color = Fore.YELLOW
                icon = "◆"
            
            print(f"{time:<20} {pair:<10} {icon} {pattern_name:<38} {bias_color}{bias:<10}{Style.RESET_ALL} {score:<8.1f} {confidence:<8.0f}")
    
    # 4. News Table
    print(f"\n{Fore.YELLOW}{'─'*80}")
    print(f"📰 NEWS TABLE")
    print(f"{'─'*80}{Style.RESET_ALL}")
    
    cursor.execute("SELECT COUNT(*) FROM news")
    count = cursor.fetchone()[0]
    print(f"Total Records: {Fore.GREEN}{count}{Style.RESET_ALL}\n")
    
    if count > 0:
        cursor.execute("""
            SELECT date, currency, title, sentiment_score
            FROM news 
            ORDER BY date DESC 
            LIMIT 10
        """)
        
        print(f"{'Date':<20} {'Currency':<10} {'Sentiment':<12} {'Headline':<50}")
        print("─" * 95)
        
        for row in cursor.fetchall():
            date, currency, headline, sentiment = row
            
            if sentiment > 0.05:
                sent_color = Fore.GREEN
                sent_label = f"+{sentiment:.3f}"
            elif sentiment < -0.05:
                sent_color = Fore.RED
                sent_label = f"{sentiment:.3f}"
            else:
                sent_color = Fore.YELLOW
                sent_label = f"{sentiment:.3f}"
            
            headline_short = headline[:50] if len(headline) <= 50 else headline[:47] + "..."
            print(f"{date:<20} {currency:<10} {sent_color}{sent_label:<12}{Style.RESET_ALL} {headline_short}")
    
    # Summary Statistics
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"📊 SUMMARY STATISTICS")
    print(f"{'='*80}{Style.RESET_ALL}\n")
    
    # Signal distribution
    cursor.execute("SELECT signal, COUNT(*) FROM signals GROUP BY signal")
    signal_counts = cursor.fetchall()
    
    if signal_counts:
        print(f"{Fore.WHITE}Signal Distribution:{Style.RESET_ALL}")
        for signal, count in signal_counts:
            if signal == "BUY":
                print(f"  {Fore.GREEN}▲ BUY:{Style.RESET_ALL}  {count}")
            elif signal == "SELL":
                print(f"  {Fore.RED}▼ SELL:{Style.RESET_ALL} {count}")
            else:
                print(f"  {Fore.YELLOW}◆ WAIT:{Style.RESET_ALL} {count}")
    
    # Pattern distribution
    cursor.execute("""
        SELECT pattern_name, COUNT(*) as cnt 
        FROM pattern_history 
        GROUP BY pattern_name 
        ORDER BY cnt DESC 
        LIMIT 5
    """)
    pattern_counts = cursor.fetchall()
    
    if pattern_counts:
        print(f"\n{Fore.WHITE}Top 5 Most Detected Patterns:{Style.RESET_ALL}")
        for pattern, count in pattern_counts:
            print(f"  • {pattern}: {count}")
    
    # Symbol coverage
    cursor.execute("SELECT DISTINCT pair FROM market_data ORDER BY pair")
    symbols = cursor.fetchall()
    
    if symbols:
        print(f"\n{Fore.WHITE}Symbols Tracked:{Style.RESET_ALL}")
        symbol_list = [s[0] for s in symbols]
        print(f"  {', '.join(symbol_list)}")
    
    # Latest timestamp
    cursor.execute("SELECT MAX(time) FROM market_data")
    latest = cursor.fetchone()[0]
    if latest:
        print(f"\n{Fore.WHITE}Latest Data Update:{Style.RESET_ALL} {latest}")
    
    # Currency coverage in news
    cursor.execute("SELECT DISTINCT currency FROM news ORDER BY currency")
    currencies = cursor.fetchall()
    
    if currencies:
        print(f"\n{Fore.WHITE}News Coverage:{Style.RESET_ALL}")
        currency_list = [c[0] for c in currencies if c[0]]
        print(f"  {', '.join(currency_list)}")
    
    conn.close()
    
    print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

if __name__ == "__main__":
    show_database_contents()
