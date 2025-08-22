"""News ranking by relevance and importance."""

import logging
from typing import List, Dict
from datetime import datetime

class NewsRanker:
    """Rank news items by relevance and importance."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def rank(self, news_items: List[Dict]) -> List[Dict]:
        """Rank news items by relevance score."""
        try:
            # Sort by relevance score (highest first)
            ranked_items = sorted(
                news_items, 
                key=lambda x: x.get('classification', {}).get('relevance_score', 0.0),
                reverse=True
            )
            
            # Add rank position
            for i, item in enumerate(ranked_items):
                item['rank'] = i + 1
            
            return ranked_items
            
        except Exception as e:
            self.logger.error(f"Error ranking news: {str(e)}")
            return news_items 