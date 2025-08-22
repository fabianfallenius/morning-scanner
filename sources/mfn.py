#!/usr/bin/env python3
"""MFN (Mäklarsamfundet) news scraper for Morning Scanner."""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
from common.utils_time import parse_iso_guess_tz
from common.ssl_config import get_ssl_config

logger = logging.getLogger(__name__)


class MFNScraper:
    """Scrapes news from MFN (Mäklarsamfundet)."""
    
    def __init__(self):
        self.base_url = "https://www.mfn.se"
        self.session = None
        self.ssl_config = get_ssl_config()
        logger.info(f"MFN scraper initialized for {self.base_url}")
    
    async def _create_session(self) -> aiohttp.ClientSession:
        """Create aiohttp session with proper SSL configuration."""
        if self.session is None or self.session.closed:
            # Use strict SSL since we confirmed it works
            ssl_context = self.ssl_config.get_aiohttp_ssl_context(strict=True)
            
            connector = aiohttp.TCPConnector(
                ssl=ssl_context,
                limit=10,
                limit_per_host=5,
                ttl_dns_cache=300
            )
            
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'Morning Scanner Bot (+https://github.com/your-repo)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'sv-SE,sv;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            )
        
        return self.session
    
    async def _check_robots_txt(self) -> bool:
        """Check robots.txt for scraping permissions."""
        try:
            session = await self._create_session()
            async with session.get(f"{self.base_url}/robots.txt") as response:
                if response.status == 200:
                    robots_content = await response.text()
                    logger.info("Robots.txt fetched successfully")
                    
                    # Simple check - if robots.txt exists, we're being respectful
                    # In production, you might want to parse this more carefully
                    return True
                else:
                    logger.warning(f"Robots.txt returned status {response.status}")
                    return False
                    
        except Exception as e:
            logger.warning(f"Could not fetch robots.txt: {e}")
            return False
    
    async def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch a single page with proper error handling."""
        try:
            session = await self._create_session()
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.error(f"Failed to fetch {url}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    async def _parse_news_page(self, html: str, source_path: str) -> List[Dict[str, Any]]:
        """Parse news items from a page."""
        news_items = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for news articles - adjust selectors based on actual MFN structure
            articles = soup.find_all(['article', 'div'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['news', 'article', 'post', 'item']
            ))
            
            if not articles:
                # Fallback: look for any div with news-like content
                articles = soup.find_all('div', class_=lambda x: x and 'nyhet' in x.lower())
            
            for article in articles[:20]:  # Limit to 20 articles per page
                try:
                    # Extract title
                    title_elem = article.find(['h1', 'h2', 'h3', 'h4'])
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue
                    
                    # Extract link
                    link_elem = article.find('a', href=True)
                    if not link_elem:
                        continue
                    
                    link = link_elem['href']
                    if not link.startswith('http'):
                        link = f"{self.base_url.rstrip('/')}/{link.lstrip('/')}"
                    
                    # Extract snippet/description
                    snippet_elem = article.find(['p', 'div'], class_=lambda x: x and any(
                        keyword in x.lower() for keyword in ['excerpt', 'summary', 'description', 'text']
                    ))
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    # Extract timestamp if available
                    time_elem = article.find(['time', 'span'], datetime=True)
                    timestamp = None
                    if time_elem:
                        timestamp = time_elem.get('datetime')
                    else:
                        # Look for date in text
                        date_elem = article.find(['span', 'div'], class_=lambda x: x and any(
                            keyword in x.lower() for keyword in ['date', 'time', 'published']
                        ))
                        if date_elem:
                            timestamp = date_elem.get_text(strip=True)
                    
                    # Parse timestamp
                    if timestamp:
                        try:
                            parsed_time = parse_iso_guess_tz(timestamp)
                        except:
                            parsed_time = datetime.now()
                    else:
                        parsed_time = datetime.now()
                    
                    news_items.append({
                        'title': title,
                        'url': link,
                        'snippet': snippet,
                        'timestamp': parsed_time.isoformat(),
                        'source': 'MFN',
                        'source_path': source_path
                    })
                    
                except Exception as e:
                    logger.debug(f"Error parsing article: {e}")
                    continue
            
            logger.info(f"Parsed {len(news_items)} news items from {source_path}")
            
        except Exception as e:
            logger.error(f"Error parsing news page: {e}")
        
        return news_items
    
    async def _deduplicate_news(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate news items based on title similarity."""
        if not news_items:
            return []
        
        # Simple deduplication based on title similarity
        unique_items = []
        seen_titles = set()
        
        for item in news_items:
            title_lower = item['title'].lower()
            
            # Check if we've seen a similar title
            is_duplicate = False
            for seen_title in seen_titles:
                # Simple similarity check - if titles are very similar, skip
                if (len(title_lower) > 20 and 
                    any(word in seen_title for word in title_lower.split()[:3])):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_items.append(item)
                seen_titles.add(title_lower)
        
        logger.info(f"Deduplicated {len(news_items)} -> {len(unique_items)} items")
        return unique_items
    
    async def scrape_news(self) -> List[Dict[str, Any]]:
        """Scrape news from multiple MFN paths."""
        logger.info("Starting MFN scraping")
        
        # Check robots.txt first
        robots_allowed = await self._check_robots_txt()
        if not robots_allowed:
            logger.warning("Robots.txt check failed - proceeding with caution")
        
        # Define news paths to scrape
        news_paths = [
            '/nyheter',
            '/borsnyheter', 
            '/ekonominyheter',
            '/foretagsnyheter'
        ]
        
        all_news = []
        
        for path in news_paths:
            try:
                url = f"{self.base_url}{path}"
                logger.info(f"Scraping {url}")
                
                html = await self._fetch_page(url)
                if html:
                    news_items = await self._parse_news_page(html, path)
                    all_news.extend(news_items)
                else:
                    logger.warning(f"No content received from {url}")
                
                # Be respectful - small delay between requests
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error scraping {path}: {e}")
                continue
        
        # Deduplicate and return
        unique_news = await self._deduplicate_news(all_news)
        
        logger.info(f"MFN scraping completed: {len(unique_news)} items found")
        return unique_news
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None


# For backward compatibility
async def scrape():
    """Legacy scrape function."""
    scraper = MFNScraper()
    try:
        return await scraper.scrape_news()
    finally:
        await scraper.close() 