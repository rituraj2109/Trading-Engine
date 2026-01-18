from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
from utils import get_db_connection, logger

class SentimentEngine:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze_text(self, text):
        """
        Returns compound score: -1 (Most Negative) to +1 (Most Positive)
        """
        if not text:
            return 0
        scores = self.analyzer.polarity_scores(text)
        return scores['compound']

    def update_sentiment_scores(self):
        """
        Read news from DB with 0 sentiment score, update them.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get news where sentiment_score is 0 (assuming newly inserted or neutral)
        # To strictly process only new ones, we might need a 'processed' flag 
        # but here we just re-process if 0 or select all since last run. 
        # For efficiency, let's just proceed.
        
        cursor.execute("SELECT id, title, source FROM news WHERE sentiment_score = 0")
        rows = cursor.fetchall()
        
        for row in rows:
            news_id, title, source = row
            score = self.analyze_text(title)
            cursor.execute("UPDATE news SET sentiment_score = ? WHERE id = ?", (score, news_id))
        
        conn.commit()
        conn.close()

    def get_currency_sentiment(self, currency, hours=24):
        """
        Aggregate sentiment for a specific currency over the last N hours.
        Returns a normalized score.
        """
        conn = get_db_connection()
        
        # Aliases for Commodities
        search_term = currency
        if currency == 'XAU': search_term = 'Gold'
        if currency == 'XAG': search_term = 'Silver'
        
        # Query: average sentiment of news
        query = f"""
            SELECT AVG(sentiment_score) as score, COUNT(*) as cnt 
            FROM news 
            WHERE (title LIKE '%{search_term}%' OR currency = '{currency}')
            AND date >= datetime('now', '-{hours} hours')
        """
        
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchone()
            if result and result[0] is not None:
                avg_score = result[0]
                count = result[1]
                # Weight by volume? Maybe. For now, just raw average.
                # If news is scarce, confidence is low.
                
                # Normalize to range -2 to +2 roughly based on intensity
                # VADER compound is -1 to 1.
                return avg_score * 2 # Scaled
        except Exception as e:
            logger.error(f"Sentiment Query Error: {e}")
            
        conn.close()
        return 0

    def get_pair_sentiment_score(self, pair):
        """
        EURUSD -> Score(EUR) - Score(USD)
        """
        base = pair[:3]
        quote = pair[3:]
        
        s_base = self.get_currency_sentiment(base)
        s_quote = self.get_currency_sentiment(quote)
        
        return s_base - s_quote
