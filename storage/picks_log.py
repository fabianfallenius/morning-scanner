"""
News picks logging and storage for the Morning Scanner application.

This module provides:
- Logging of news picks to CSV
- Historical tracking of positive news
- Data export functionality
"""

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from common.config import get_config
from common.utils_time import now_se


class PicksLogger:
    """
    Log and store news picks for future reference.
    
    This class provides:
    - CSV-based storage of news picks
    - Historical tracking
    - Data export functionality
    """
    
    def __init__(self, log_file: Optional[str] = None):
        """Initialize the picks logger."""
        self.logger = logging.getLogger(__name__)
        self.config = get_config()
        
        # Set log file path
        if log_file is None:
            log_file = self.config.PICKS_LOG_FILE
        
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize CSV file if it doesn't exist
        self._initialize_csv()
        
        self.logger.info(f"Picks logger initialized: {self.log_file}")
    
    def _initialize_csv(self):
        """Initialize the CSV file with headers if it doesn't exist."""
        if not self.log_file.exists():
            headers = [
                'timestamp', 'title', 'url', 'source', 'relevance_score',
                'sentiment_score', 'impact_level', 'has_catalyst', 'categories'
            ]
            
            with open(self.log_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
            
            self.logger.info(f"Created new picks log file: {self.log_file}")
    
    def log_pick(self, title: str, url: str, source: str, relevance_score: float,
                  sentiment_score: float, impact_level: str, has_catalyst: bool,
                  categories: Optional[List[str]] = None):
        """
        Log a news pick to the CSV file.
        
        Args:
            title (str): News title
            url (str): News URL
            source (str): News source
            relevance_score (float): Relevance score (0.0 to 1.0)
            sentiment_score (float): Sentiment score (-1.0 to 1.0)
            impact_level (str): Impact level ('low', 'medium', 'high')
            has_catalyst (bool): Whether it's a catalyst event
            categories (List[str], optional): News categories
        """
        try:
            timestamp = now_se().isoformat()
            categories_str = ';'.join(categories) if categories else ''
            
            row = [
                timestamp,
                title[:200],  # Limit title length
                url,
                source,
                f"{relevance_score:.3f}",
                f"{sentiment_score:.3f}",
                impact_level,
                'Yes' if has_catalyst else 'No',
                categories_str
            ]
            
            with open(self.log_file, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(row)
            
            self.logger.debug(f"Logged pick: {title[:50]}...")
            
        except Exception as e:
            self.logger.error(f"Error logging pick: {str(e)}")
    
    def get_recent_picks(self, days: int = 7) -> List[Dict]:
        """
        Get recent picks from the last N days.
        
        Args:
            days (int): Number of days to look back
            
        Returns:
            List[Dict]: Recent picks
        """
        try:
            if not self.log_file.exists():
                return []
            
            picks = []
            cutoff_date = now_se().date()
            
            with open(self.log_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    try:
                        # Parse timestamp
                        timestamp = datetime.fromisoformat(row['timestamp'])
                        pick_date = timestamp.date()
                        
                        # Check if within date range
                        if (cutoff_date - pick_date).days <= days:
                            picks.append({
                                'timestamp': row['timestamp'],
                                'title': row['title'],
                                'url': row['url'],
                                'source': row['source'],
                                'relevance_score': float(row['relevance_score']),
                                'sentiment_score': float(row['sentiment_score']),
                                'impact_level': row['impact_level'],
                                'has_catalyst': row['has_catalyst'] == 'Yes',
                                'categories': row['categories'].split(';') if row['categories'] else []
                            })
                    except Exception as e:
                        self.logger.debug(f"Error parsing row: {str(e)}")
                        continue
            
            # Sort by timestamp (newest first)
            picks.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return picks
            
        except Exception as e:
            self.logger.error(f"Error reading recent picks: {str(e)}")
            return []
    
    def get_picks_by_source(self, source: str, days: int = 30) -> List[Dict]:
        """
        Get picks from a specific source.
        
        Args:
            source (str): Source name to filter by
            days (int): Number of days to look back
            
        Returns:
            List[Dict]: Picks from the specified source
        """
        all_picks = self.get_recent_picks(days)
        return [pick for pick in all_picks if pick['source'].lower() == source.lower()]
    
    def get_high_impact_picks(self, days: int = 30) -> List[Dict]:
        """
        Get high-impact picks from the last N days.
        
        Args:
            days (int): Number of days to look back
            
        Returns:
            List[Dict]: High-impact picks
        """
        all_picks = self.get_recent_picks(days)
        return [pick for pick in all_picks if pick['impact_level'] == 'high']
    
    def get_catalyst_picks(self, days: int = 30) -> List[Dict]:
        """
        Get catalyst event picks from the last N days.
        
        Args:
            days (int): Number of days to look back
            
        Returns:
            List[Dict]: Catalyst event picks
        """
        all_picks = self.get_recent_picks(days)
        return [pick for pick in all_picks if pick['has_catalyst']]
    
    def get_statistics(self, days: int = 30) -> Dict:
        """
        Get statistics about logged picks.
        
        Args:
            days (int): Number of days to analyze
            
        Returns:
            Dict: Pick statistics
        """
        picks = self.get_recent_picks(days)
        
        if not picks:
            return {
                'total_picks': 0,
                'sources': {},
                'impact_distribution': {},
                'catalyst_events': 0,
                'avg_relevance': 0.0,
                'avg_sentiment': 0.0
            }
        
        # Source distribution
        sources = {}
        for pick in picks:
            source = pick['source']
            sources[source] = sources.get(source, 0) + 1
        
        # Impact distribution
        impact_distribution = {}
        for pick in picks:
            impact = pick['impact_level']
            impact_distribution[impact] = impact_distribution.get(impact, 0) + 1
        
        # Catalyst events
        catalyst_events = sum(1 for pick in picks if pick['has_catalyst'])
        
        # Averages
        avg_relevance = sum(pick['relevance_score'] for pick in picks) / len(picks)
        avg_sentiment = sum(pick['sentiment_score'] for pick in picks) / len(picks)
        
        return {
            'total_picks': len(picks),
            'sources': sources,
            'impact_distribution': impact_distribution,
            'catalyst_events': catalyst_events,
            'avg_relevance': round(avg_relevance, 3),
            'avg_sentiment': round(avg_sentiment, 3)
        }
    
    def export_picks(self, output_file: str, days: int = 30):
        """
        Export picks to a different format.
        
        Args:
            output_file (str): Output file path
            days (int): Number of days to export
        """
        try:
            picks = self.get_recent_picks(days)
            
            if output_file.endswith('.json'):
                import json
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(picks, f, indent=2, ensure_ascii=False)
            
            elif output_file.endswith('.csv'):
                import shutil
                shutil.copy2(self.log_file, output_file)
            
            else:
                self.logger.warning(f"Unsupported export format: {output_file}")
                return
            
            self.logger.info(f"Exported {len(picks)} picks to {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error exporting picks: {str(e)}")
    
    def clear_old_picks(self, days: int = 90):
        """
        Clear picks older than N days.
        
        Args:
            days (int): Age threshold in days
        """
        try:
            if not self.log_file.exists():
                return
            
            # Read all picks
            all_picks = []
            cutoff_date = now_se().date()
            
            with open(self.log_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                headers = reader.fieldnames
                
                for row in reader:
                    try:
                        timestamp = datetime.fromisoformat(row['timestamp'])
                        pick_date = timestamp.date()
                        
                        # Keep picks within threshold
                        if (cutoff_date - pick_date).days <= days:
                            all_picks.append(row)
                    except Exception as e:
                        self.logger.debug(f"Error parsing row during cleanup: {str(e)}")
                        continue
            
            # Rewrite file with kept picks
            with open(self.log_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(all_picks)
            
            self.logger.info(f"Cleared old picks, kept {len(all_picks)} recent items")
            
        except Exception as e:
            self.logger.error(f"Error clearing old picks: {str(e)}")


# Global instance for easy access
picks_logger = PicksLogger()


def get_picks_logger() -> PicksLogger:
    """
    Get the global picks logger instance.
    
    Returns:
        PicksLogger: Picks logger instance
    """
    return picks_logger 