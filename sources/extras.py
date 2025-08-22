#!/usr/bin/env python3
"""Extra news sources scraper for Morning Scanner."""

import asyncio
import aiohttp
import logging
import feedparser
from typing import List, Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from common.utils_time import parse_iso_guess_tz
from common.ssl_config import get_ssl_config

logger = logging.getLogger(__name__)


class ExtraSourcesScraper:
    """Scrapes news from additional sources like RSS feeds and APIs."""
    
    def __init__(self):
        self.ssl_config = get_ssl_config()
        self.session = None
        
        # RSS feeds to monitor
        self.rss_feeds = {
            'SVT Ekonomi': 'https://www.svt.se/nyheter/rss.xml',
            'DN Ekonomi': 'https://www.dn.se/rss/ekonomi/',
            'SVT Näringsliv': 'https://www.svt.se/nyheter/rss.xml?section=naringsliv',
            'Aftonbladet Ekonomi': 'https://www.aftonbladet.se/ekonomi/rss.xml',
            
            # Working Swedish financial news:
            'Sveriges Radio Ekonomi': 'https://sverigesradio.se/api/rss/program/83',
            'Expressen Ekonomi': 'https://www.expressen.se/ekonomi/rss.xml',
            'SVT Sport': 'https://www.svt.se/nyheter/rss.xml?section=sport',
            'SVT Kultur': 'https://www.svt.se/nyheter/rss.xml?section=kultur',
            
            # International financial news:
            'Reuters Business': 'https://feeds.reuters.com/reuters/businessNews',
            'Bloomberg Markets': 'https://feeds.bloomberg.com/markets/news.rss',
            'Financial Times': 'https://www.ft.com/rss/home',
            
            # Swedish company news:
            'Ericsson Investor': 'https://www.ericsson.com/en/investors/financial-reports',
            'Volvo Cars': 'https://www.volvocars.com/intl/news',
            'SEB Group': 'https://sebgroup.com/press-and-news'
        }
        
        # API endpoints (placeholder for future use)
        self.api_endpoints = {
            'Riksbanken': 'https://www.riksbank.se/sv/nyheter-och-press/nyheter/',
            'Finansinspektionen': 'https://www.fi.se/sv/nyheter/'
        }
        
        logger.info(f"Extra sources scraper initialized with {len(self.rss_feeds)} RSS feeds")
    
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
                    'Accept': 'application/rss+xml,application/xml,text/xml,*/*;q=0.9',
                    'Accept-Language': 'sv-SE,sv;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive'
                }
            )
        
        return self.session
    
    async def _fetch_rss_feed(self, name: str, url: str) -> List[Dict[str, Any]]:
        """Fetch and parse an RSS feed."""
        try:
            session = await self._create_session()
            logger.info(f"Fetching RSS feed: {name} ({url})")
            
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Parse RSS content
                    feed = feedparser.parse(content)
                    
                    if feed.bozo:
                        logger.warning(f"RSS feed {name} has parsing errors")
                    
                    news_items = []
                    for entry in feed.entries[:10]:  # Limit to 10 items per feed
                        try:
                            # Extract basic info
                            title = entry.get('title', '').strip()
                            if not title or len(title) < 10:
                                continue
                            
                            link = entry.get('link', '')
                            if not link:
                                continue
                            
                            # Extract description/summary
                            description = entry.get('description', '')
                            if not description:
                                description = entry.get('summary', '')
                            
                            # Extract timestamp
                            timestamp = None
                            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                timestamp = datetime(*entry.published_parsed[:6]).isoformat()
                            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                                timestamp = datetime(*entry.updated_parsed[:6]).isoformat()
                            else:
                                timestamp = datetime.now().isoformat()
                            
                            # Extract author if available
                            author = entry.get('author', '')
                            
                            news_items.append({
                                'title': title,
                                'url': link,
                                'snippet': description,
                                'timestamp': timestamp,
                                'source': name,
                                'author': author,
                                'feed_type': 'rss'
                            })
                            
                        except Exception as e:
                            logger.debug(f"Error parsing RSS entry from {name}: {e}")
                            continue
                    
                    logger.info(f"Parsed {len(news_items)} items from RSS feed: {name}")
                    return news_items
                    
                else:
                    logger.warning(f"RSS feed {name} returned status {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching RSS feed {name}: {e}")
            return []
    
    async def _fetch_api_content(self, name: str, url: str) -> List[Dict[str, Any]]:
        """Fetch content from API endpoints (placeholder for future implementation)."""
        try:
            session = await self._create_session()
            logger.info(f"Fetching API content: {name} ({url})")
            
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Parse HTML content from API responses
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Look for news items
                    news_items = []
                    articles = soup.find_all(['article', 'div'], class_=lambda x: x and any(
                        keyword in x.lower() for keyword in ['news', 'article', 'post', 'item', 'nyhet']
                    ))
                    
                    for article in articles[:15]:  # Limit to 15 items
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
                                link = f"{url.rstrip('/')}/{link.lstrip('/')}"
                            
                            # Extract snippet
                            snippet_elem = article.find(['p', 'div'], class_=lambda x: x and any(
                                keyword in x.lower() for keyword in ['excerpt', 'summary', 'description']
                            ))
                            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                            
                            news_items.append({
                                'title': title,
                                'url': link,
                                'snippet': snippet,
                                'timestamp': datetime.now().isoformat(),
                                'source': name,
                                'feed_type': 'api'
                            })
                            
                        except Exception as e:
                            logger.debug(f"Error parsing API article from {name}: {e}")
                            continue
                    
                    logger.info(f"Parsed {len(news_items)} items from API: {name}")
                    return news_items
                    
                else:
                    logger.warning(f"API {name} returned status {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching API content {name}: {e}")
            return []
    
    async def _deduplicate_news(self, all_news: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate news items across all sources."""
        if not all_news:
            return []
        
        # Simple deduplication based on title similarity
        unique_items = []
        seen_titles = set()
        
        for item in all_news:
            title_lower = item['title'].lower()
            
            # Check if we've seen a similar title
            is_duplicate = False
            for seen_title in seen_titles:
                # Simple similarity check
                if (len(title_lower) > 20 and 
                    any(word in seen_title for word in title_lower.split()[:3])):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_items.append(item)
                seen_titles.add(title_lower)
        
        logger.info(f"Deduplicated {len(all_news)} -> {len(unique_items)} items")
        return unique_items
    
    async def scrape_news(self) -> List[Dict[str, Any]]:
        """Scrape news from all extra sources."""
        logger.info("Starting extra sources scraping")
        
        all_news = []
        
        # Scrape RSS feeds
        for name, url in self.rss_feeds.items():
            try:
                news_items = await self._fetch_rss_feed(name, url)
                all_news.extend(news_items)
                
                # Be respectful - small delay between requests
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error scraping RSS feed {name}: {e}")
                continue
        
        # Scrape API endpoints (placeholder)
        for name, url in self.api_endpoints.items():
            try:
                news_items = await self._fetch_api_content(name, url)
                all_news.extend(news_items)
                
                # Be respectful - small delay between requests
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error scraping API {name}: {e}")
                continue
        
        # Deduplicate and return
        unique_news = await self._deduplicate_news(all_news)
        
        logger.info(f"Extra sources scraping completed: {len(unique_news)} items found")
        return unique_news
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None


# For backward compatibility
async def scrape():
    """Legacy scrape function."""
    scraper = ExtraSourcesScraper()
    try:
        return await scraper.scrape_news()
    finally:
        await scraper.close() 