"""
Morning Scanner - Swedish Financial News Scanner

This application:
1. Scrapes news from Swedish financial sources
2. Analyzes content using Swedish financial keywords
3. Classifies and ranks news by relevance
4. Sends daily reports via email
5. Identifies positive stock opportunities

Usage:
    python main.py                    # Run once
    python scripts/run_once.py        # Run once (alternative)
    python scripts/validate_sources.py # Test news sources
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

from common.config import get_config
from common.logging_setup import setup_logging
from common.utils_time import now_se
from sources.mfn import MFNScraper
from sources.di_morgonkoll import DIMorgonkollScraper
from sources.di_main import DIMainScraper
from sources.extras import ExtraSourcesScraper
from mapping.map_company import CompanyMapper
from nlp.classify import get_news_classifier
from output.sender_email import get_email_sender
from output.sender_telegram import get_telegram_sender
from storage.picks_log import PicksLogger


class MorningScanner:
    """
    Main application for scanning Swedish financial news.
    
    This class orchestrates:
    - News collection from multiple sources
    - Content analysis and classification
    - Relevance scoring and ranking
    - Report generation and delivery
    """
    
    def __init__(self):
        """Initialize the Morning Scanner."""
        self.logger = logging.getLogger(__name__)
        self.config = get_config()
        
        # Setup logging
        setup_logging()
        
        # Initialize components
        self.company_mapper = CompanyMapper()
        self.news_classifier = get_news_classifier()
        
        # Initialize news sources
        self.news_sources = [
            MFNScraper(),
            DIMorgonkollScraper(),
            DIMainScraper(),
            ExtraSourcesScraper()
        ]
        
        # Initialize output senders
        self.email_sender = get_email_sender() if self.config.EMAIL_ENABLED else None
        self.telegram_sender = get_telegram_sender() if self.config.TELEGRAM_ENABLED else None
        
        # Initialize storage
        self.picks_logger = PicksLogger()
        
        self.logger.info(f"Morning Scanner initialized at {now_se().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    async def run(self) -> bool:
        """
        Run the complete Morning Scanner pipeline.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info("Starting Morning Scanner")
            
            # Step 1: Collect news from sources
            self.logger.info("Step 1: Collecting news from sources...")
            
            all_news = []
            
            # Collect from each source
            for i, scraper in enumerate(self.news_sources):
                try:
                    source_name = scraper.__class__.__name__
                    self.logger.info(f"Collecting from {source_name}...")
                    
                    news_items = await scraper.scrape_news()
                    
                    if news_items:
                        all_news.extend(news_items)
                        self.logger.info(f"Collected {len(news_items)} items from {source_name}")
                    else:
                        self.logger.info(f"Collected 0 items from {source_name}")
                        
                except Exception as e:
                    self.logger.error(f"Error collecting from {scraper.__class__.__name__}: {e}")
                    continue
            
            if not all_news:
                self.logger.warning("No news collected from any source")
                return False
            
            # Step 2: Classify and analyze news
            self.logger.info("Step 2: Classifying and analyzing news...")
            classified_news = self._classify_news(all_news)
            
            # Step 3: Generate insights
            self.logger.info("Step 3: Generating insights...")
            insights = self.news_classifier.get_enhanced_insights(classified_news)
            
            # Step 4: Log picks
            self.logger.info("Step 4: Logging news picks...")
            self._log_picks(classified_news)
            
            # Step 5: Send reports
            self.logger.info("Step 5: Sending reports...")
            await self._send_reports(classified_news, insights)
            
            self.logger.info("Morning Scanner completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error running Morning Scanner: {str(e)}")
            return False
    
    async def _collect_news(self) -> List[Dict]:
        """
        Collect news from all sources.
        
        Returns:
            List[Dict]: Combined news items from all sources
        """
        all_news = []
        
        for source in self.news_sources:
            try:
                source_name = source.__class__.__name__
                self.logger.info(f"Collecting from {source_name}...")
                
                # Collect news from source
                if hasattr(source, 'scrape_news'):
                    news_items = await source.scrape_news(max_items=50)
                else:
                    # Fallback for older scrapers
                    news_items = await source.scrape()
                
                self.logger.info(f"Collected {len(news_items)} items from {source_name}")
                all_news.extend(news_items)
                
            except Exception as e:
                self.logger.error(f"Error collecting from {source_name}: {str(e)}")
                continue
        
        return all_news
    
    def _classify_news(self, news_items: List[Dict]) -> List[Dict]:
        """
        Classify and analyze news items.
        
        Args:
            news_items (List[Dict]): Raw news items
            
        Returns:
            List[Dict]: News items with classification added
        """
        classified_news = []
        
        for item in news_items:
            try:
                # Extract text for classification
                title = item.get('title', '')
                snippet = item.get('snippet', '')
                content = item.get('content', '')
                
                # Classify the news
                classification = self.news_classifier.classify_news(title, content, snippet)
                
                # Add classification to item
                item['classification'] = classification
                classified_news.append(item)
                
            except Exception as e:
                self.logger.error(f"Error classifying news item: {str(e)}")
                continue
        
        # Sort by relevance score (highest first)
        classified_news.sort(key=lambda x: getattr(x.get('classification'), 'relevance_score', 0), reverse=True)
        
        return classified_news
    
    def _log_picks(self, classified_news: List[Dict]):
        """Log news picks to storage."""
        try:
            # Filter for high-relevance news
            high_relevance_news = [
                item for item in classified_news
                if item.get('classification', {}).get('relevance_score', 0) >= 0.3
            ]
            
            # Log to storage
            for item in high_relevance_news:
                self.picks_logger.log_pick(
                    title=item.get('title', ''),
                    url=item.get('url', item.get('link', '')),
                    source=item.get('source', 'Unknown'),
                    relevance_score=item.get('classification', {}).get('relevance_score', 0),
                    sentiment_score=item.get('classification', {}).get('sentiment_score', 0),
                    impact_level=item.get('classification', {}).get('impact_level', 'low'),
                    has_catalyst=item.get('classification', {}).get('has_catalyst', False)
                )
            
            self.logger.info(f"Logged {len(high_relevance_news)} high-relevance picks")
            
        except Exception as e:
            self.logger.error(f"Error logging picks: {str(e)}")
    
    async def _send_reports(self, classified_news: List[Dict], insights: Dict):
        """Send reports via configured channels."""
        try:
            # Send email report
            if self.email_sender:
                self.logger.info("Sending email report...")
                email_success = self.email_sender.send_daily_report(classified_news, insights)
                
                if email_success:
                    self.logger.info("Email report sent successfully")
                else:
                    self.logger.error("Failed to send email report")
            
            # Send Telegram report
            if self.telegram_sender:
                self.logger.info("Sending Telegram report...")
                # TODO: Implement Telegram sending
                self.logger.info("Telegram sending not yet implemented")
            
        except Exception as e:
            self.logger.error(f"Error sending reports: {str(e)}")
    
    def get_summary(self) -> Dict:
        """Get a summary of the scanner status."""
        return {
            'status': 'initialized',
            'email_enabled': self.config.EMAIL_ENABLED,
            'telegram_enabled': self.config.TELEGRAM_ENABLED,
            'news_sources': len(self.news_sources),
            'company_mapping': len(self.company_mapper.company_mapping) if self.company_mapper.company_mapping else 0,
            'config_timezone': self.config.TZ,
            'schedule_time': f"{self.config.RUN_HOUR:02d}:{self.config.RUN_MINUTE:02d}"
        }


async def main():
    """Main entry point for the Morning Scanner."""
    try:
        # Create and run scanner
        scanner = MorningScanner()
        
        # Show summary
        summary = scanner.get_summary()
        print("🌅 Morning Scanner - Swedish Financial News Scanner")
        print("=" * 60)
        print(f"Status: {summary['status']}")
        print(f"Email: {'✅ Enabled' if summary['email_enabled'] else '❌ Disabled'}")
        print(f"Telegram: {'✅ Enabled' if summary['telegram_enabled'] else '❌ Disabled'}")
        print(f"News Sources: {summary['news_sources']}")
        print(f"Company Mapping: {summary['company_mapping']} companies")
        print(f"Timezone: {summary['config_timezone']}")
        print(f"Schedule: {summary['schedule_time']}")
        print("=" * 60)
        
        # Run scanner
        success = await scanner.run()
        
        if success:
            print("🎉 Morning Scanner completed successfully!")
            sys.exit(0)
        else:
            print("❌ Morning Scanner encountered errors")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Morning Scanner interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"💥 Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 