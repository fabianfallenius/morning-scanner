#!/usr/bin/env python3
"""Extra news sources scraper for Morning Scanner."""

import asyncio
import aiohttp
import logging
import os
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
        
        # RSS feeds to monitor - ONLY WORKING FEEDS
        self.rss_feeds = {
            # Swedish Financial News (Working)
            'SVT Ekonomi': 'https://www.svt.se/nyheter/rss.xml',
            'DN Ekonomi': 'https://www.dn.se/rss/ekonomi/',
            'SVT Näringsliv': 'https://www.svt.se/nyheter/rss.xml?section=naringsliv',
            'Aftonbladet Ekonomi': 'https://www.aftonbladet.se/ekonomi/rss.xml',
            
            # Swedish News Sections (Working)
            'SVT Sport': 'https://www.svt.se/nyheter/rss.xml?section=sport',
            'SVT Kultur': 'https://www.svt.se/nyheter/rss.xml?section=kultur',
            
            # International Financial News (Working)
            'Bloomberg Markets': 'https://feeds.bloomberg.com/markets/news.rss',
            'Financial Times': 'https://www.ft.com/rss/home'
        }
        
        # API endpoints - REMOVED (all were failing)
        self.api_endpoints = {}
        
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
                            
                            # Extract content if available (some RSS feeds include full content)
                            content = entry.get('content', [{}])[0].get('value', '') if entry.get('content') else ''
                            if not content:
                                content = entry.get('encoded', '')  # Try encoded content
                            
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
                            
                            # Extract categories/tags if available
                            categories = []
                            if hasattr(entry, 'tags'):
                                categories = [tag.term for tag in entry.tags if hasattr(tag, 'term')]
                            elif hasattr(entry, 'category'):
                                categories = [entry.category]
                            
                            news_items.append({
                                'title': title,
                                'url': link,
                                'snippet': description,
                                'content': content,  # Add full content when available
                                'timestamp': timestamp,
                                'source': name,
                                'author': author,
                                'categories': categories,
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
    
    async def _fetch_article_content(self, url: str, timeout: int = 5) -> str:
        """Fetch full article content from a URL."""
        try:
            session = await self._create_session()
            logger.debug(f"Fetching article content: {url}")
            
            # Use shorter timeout for GitHub Actions compatibility
            action_timeout = aiohttp.ClientTimeout(total=timeout, connect=timeout)
            
            async with session.get(url, timeout=action_timeout) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Parse HTML and extract main content
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Remove unwanted elements
                    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                        element.decompose()
                    
                    # Try to find main article content
                    content_selectors = [
                        'article', '.article-content', '.post-content', '.entry-content',
                        '.news-content', '.story-content', '.content', 'main',
                        '[class*="content"]', '[class*="article"]', '[class*="post"]'
                    ]
                    
                    article_content = ""
                    for selector in content_selectors:
                        content_elem = soup.select_one(selector)
                        if content_elem:
                            # Get all text from paragraphs
                            paragraphs = content_elem.find_all('p')
                            if paragraphs:
                                article_content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                                break
                    
                    # If no specific content found, get all paragraph text
                    if not article_content:
                        paragraphs = soup.find_all('p')
                        article_content = ' '.join([p.get_text(strip=True) for p in paragraphs])
                    
                    # Clean and limit content length
                    article_content = ' '.join(article_content.split())[:2000]  # Limit to ~2000 chars
                    
                    return article_content
                    
                else:
                    logger.debug(f"Failed to fetch article content from {url}: {response.status}")
                    return ""
                    
        except Exception as e:
            logger.debug(f"Error fetching article content from {url}: {e}")
            return ""
    
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
        """Scrape news from all configured sources."""
        all_news = []
        
        # Check if running in GitHub Actions
        is_github_actions = os.environ.get('GITHUB_ACTIONS', 'false').lower() == 'true'
        
        if is_github_actions:
            logger.info("Running in GitHub Actions - using lightweight mode (RSS only)")
        
        # Fetch from RSS feeds
        for name, url in self.rss_feeds.items():
            try:
                news_items = await self._fetch_rss_feed(name, url)
                
                # Enhance with article content for high-priority feeds (only in non-GitHub Actions environment)
                # Skip content fetching in GitHub Actions to avoid timeouts and failures
                if (name in ['SVT Ekonomi', 'DN Ekonomi', 'SVT Näringsliv'] and 
                    not is_github_actions):
                    for item in news_items[:3]:  # Reduced from 5 to 3 for faster processing
                        if item.get('url'):
                            try:
                                # Only fetch if we don't already have content from RSS
                                if not item.get('content'):
                                    article_content = await self._fetch_article_content(item['url'])
                                    if article_content:
                                        item['content'] = article_content
                                        logger.debug(f"Enhanced {name} article with content ({len(article_content)} chars)")
                            except Exception as e:
                                logger.debug(f"Failed to fetch content for {name}: {e}")
                                continue
                elif is_github_actions:
                    # In GitHub Actions mode, remove any existing content to ensure lightweight operation
                    for item in news_items:
                        if 'content' in item:
                            del item['content']
                
                all_news.extend(news_items)
                
            except Exception as e:
                logger.error(f"Error scraping {name}: {e}")
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