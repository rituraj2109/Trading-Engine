from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
from utils import logger

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
        from utils import get_mongo_db
        db_mongo = get_mongo_db()
        if db_mongo is None:
            return

        # Get news where sentiment_score is 0
        cursor = db_mongo.news.find({"sentiment_score": 0})
        
        count = 0
        for doc in cursor:
            news_id = doc['id']
            title = doc.get('title', '')
            score = self.analyze_text(title)
            
            db_mongo.news.update_one(
                {"id": news_id},
                {"$set": {"sentiment_score": score}}
            )
            count += 1
            
        if count > 0:
            logger.info(f"Updated sentiment for {count} news items.")

    def get_currency_sentiment(self, currency, hours=24):
        """
        Aggregate sentiment for a specific currency over the last N hours.
        Returns a normalized score.
        """
        from utils import get_mongo_db
        db_mongo = get_mongo_db()
        if db_mongo is None:
            return 0
        
        # Aliases for Commodities
        search_term = currency
        if currency == 'XAU': search_term = 'Gold'
        if currency == 'XAG': search_term = 'Silver'
        
        # Calculate time threshold
        from datetime import datetime, timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        cutoff_str = cutoff_time.isoformat() # Assuming we store as ISO strings

        # Pipeline to filter and average
        pipeline = [
            {
                "$match": {
                    "$or": [
                        {"title": {"$regex": search_term, "$options": "i"}},
                        {"currency": currency}
                    ],
                    "date": {"$gte": cutoff_str}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg_score": {"$avg": "$sentiment_score"},
                    "count": {"$sum": 1}
                }
            }
        ]
        
        try:
            result = list(db_mongo.news.aggregate(pipeline))
            if result:
                avg_score = result[0]['avg_score'] or 0
                return avg_score * 2 # Scaled
        except Exception as e:
            logger.error(f"Sentiment Query Error: {e}")
            
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
