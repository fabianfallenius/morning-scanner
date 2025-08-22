#!/usr/bin/env python3
"""Validate news sources and test scraping."""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sources.mfn import MFNScraper
from sources.di_morgonkoll import DIMorgonkollScraper
from sources.extras import ExtraSourcesScraper

async def validate_sources():
    """Test all news sources."""
    print("=== VALIDATING NEWS SOURCES ===")
    
    scrapers = [
        ("MFN", MFNScraper()),
        ("DI Morgonkoll", DIMorgonkollScraper()),
        ("Extra Sources", ExtraSourcesScraper())
    ]
    
    for name, scraper in scrapers:
        print(f"\nTesting {name}...")
        try:
            news_items = await scraper.scrape()
            print(f"✓ {name}: {len(news_items)} items found")
        except Exception as e:
            print(f"✗ {name}: Error - {str(e)}")

if __name__ == "__main__":
    asyncio.run(validate_sources()) 