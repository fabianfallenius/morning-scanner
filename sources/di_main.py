#!/usr/bin/env python3
"""
DI Main Website Scraper - Scrapes www.di.se for business and financial news
"""

import asyncio
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from common.ssl_config import get_ssl_config
from common.utils_time import now_se

logger = logging.getLogger(__name__)


class DIMainScraper:
    """Scraper for the main DI website (www.di.se)."""
    
    def __init__(self):
        self.ssl_config = get_ssl_config()
        self.session = None
        self.base_url = "https://www.di.se"
        
        # Main news sections to scrape - UPDATED with working sections
        self.news_sections = [
            '/nyheter/',
            '/bors/',
            '/amnen/privatekonomi/',
            '/amnen/hallbart-naringsliv/',
            '/amnen/tech-och-strategi/'
        ]
        
        logger.info("DI Main scraper initialized")
    
    async def _create_session(self) -> aiohttp.ClientSession:
        """Create aiohttp session with proper SSL configuration."""
        if self.session is None or self.session.closed:
            # Use strict SSL for DI website
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
                    'User-Agent': 'Morning Scanner Bot (+https://github.com/fabianfallenius/morning-scanner)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'sv-SE,sv;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            )
        
        return self.session
    
    async def scrape_news(self) -> List[Dict[str, Any]]:
        """Scrape news from the main DI website."""
        try:
            session = await self._create_session()
            all_news = []
            
            logger.info("🔍 Scanning DI Main Website...")
            
            # Scrape each news section
            for section in self.news_sections:
                try:
                    section_url = urljoin(self.base_url, section)
                    logger.info(f"  📰 Scraping section: {section}")
                    
                    section_news = await self._scrape_section(session, section_url, section)
                    all_news.extend(section_news)
                    
                    # Small delay between sections
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error scraping DI section {section}: {e}")
                    continue
            
            # Deduplicate news items
            unique_news = self._deduplicate_news(all_news)
            
            logger.info(f"   ✅ Found {len(unique_news)} articles from DI Main Website")
            return unique_news
            
        except Exception as e:
            logger.error(f"Error scraping DI main website: {e}")
            return []
        finally:
            # Ensure session is closed
            if session and not session.closed:
                await session.close()
    
    async def _scrape_section(self, session: aiohttp.ClientSession, url: str, section_name: str) -> List[Dict[str, Any]]:
        """Scrape a specific news section."""
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    return await self._parse_section_page(content, url, section_name)
                else:
                    logger.warning(f"DI section {section_name} returned status {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching DI section {section_name}: {e}")
            return []
    
    async def _parse_section_page(self, content: str, url: str, section_name: str) -> List[Dict[str, Any]]:
        """Parse the HTML content of a DI section page."""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            news_items = []
            
            # Look for article containers - DI uses various article selectors
            article_selectors = [
                'article',
                '.article-item',
                '.news-item',
                '.story-item',
                '.content-item',
                '[data-testid*="article"]',
                '[class*="article"]',
                '[class*="news"]',
                '[class*="story"]'
            ]
            
            articles = []
            for selector in article_selectors:
                articles.extend(soup.select(selector))
                if articles:  # If we found articles, stop looking
                    break
            
            # If no articles found with selectors, try broader approach
            if not articles:
                # Look for any div that might contain article links
                articles = soup.find_all(['div', 'article'], class_=re.compile(r'(article|news|story|content)', re.I))
            
            for article in articles[:15]:  # Limit to 15 articles per section
                try:
                    news_item = self._extract_news_item(article, section_name)
                    if news_item:
                        news_items.append(news_item)
                except Exception as e:
                    logger.debug(f"Error extracting article from {section_name}: {e}")
                    continue
            
            return news_items
            
        except Exception as e:
            logger.error(f"Error parsing DI section {section_name}: {e}")
            return []
    
    def _extract_news_item(self, article_element, section_name: str) -> Optional[Dict[str, Any]]:
        """Extract news item from an article element."""
        try:
            # Find the article link
            link_elem = article_element.find('a', href=True)
            if not link_elem:
                return None
            
            url = link_elem.get('href', '')
            if not url:
                return None
            
            # Make URL absolute if it's relative
            if url.startswith('/'):
                url = urljoin(self.base_url, url)
            elif not url.startswith('http'):
                url = urljoin(self.base_url, '/' + url)
            
            # Extract title
            title = self._extract_title(link_elem)
            if not title or len(title.strip()) < 10:
                return None
            
            # Extract snippet/description
            snippet = self._extract_snippet(article_element)
            
            # Extract timestamp
            timestamp = self._extract_timestamp(article_element)
            
            # Extract image if available
            image_url = self._extract_image(article_element)
            
            # Create news item
            news_item = {
                'title': title.strip(),
                'url': url,
                'snippet': snippet.strip() if snippet else '',
                'source': f'DI {section_name.replace("/", "").title()}',
                'timestamp': timestamp,
                'image_url': image_url,
                'section': section_name.replace('/', '').title()
            }
            
            return news_item
            
        except Exception as e:
            logger.debug(f"Error extracting news item: {e}")
            return None
    
    def _extract_title(self, link_elem) -> str:
        """Extract title from link element."""
        # Try different title selectors
        title_selectors = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            '.title', '.headline', '.article-title',
            '[class*="title"]', '[class*="headline"]'
        ]
        
        for selector in title_selectors:
            title_elem = link_elem.select_one(selector)
            if title_elem and title_elem.get_text().strip():
                return title_elem.get_text().strip()
        
        # If no title element found, use link text
        link_text = link_elem.get_text().strip()
        if link_text:
            return link_text
        
        # Try to find title in parent elements
        parent = link_elem.parent
        for _ in range(3):  # Look up to 3 levels up
            if parent:
                title_elem = parent.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if title_elem and title_elem.get_text().strip():
                    return title_elem.get_text().strip()
                parent = parent.parent
        
        return ""
    
    def _extract_snippet(self, article_element) -> str:
        """Extract snippet/description from article element."""
        # Try different snippet selectors
        snippet_selectors = [
            '.excerpt', '.summary', '.description', '.snippet',
            '.article-excerpt', '.news-excerpt', '.story-excerpt',
            'p', '.lead', '[class*="excerpt"]', '[class*="summary"]'
        ]
        
        for selector in snippet_selectors:
            snippet_elem = article_element.select_one(selector)
            if snippet_elem:
                text = snippet_elem.get_text().strip()
                if text and len(text) > 20:
                    return text
        
        # If no snippet found, try to get first paragraph
        first_p = article_element.find('p')
        if first_p:
            text = first_p.get_text().strip()
            if text and len(text) > 20:
                return text
        
        return ""
    
    def _extract_timestamp(self, article_element) -> Optional[str]:
        """Extract timestamp from article element."""
        # Try different timestamp selectors
        time_selectors = [
            'time', '.timestamp', '.date', '.published',
            '.article-date', '.news-date', '.story-date',
            '[datetime]', '[class*="date"]', '[class*="time"]'
        ]
        
        for selector in time_selectors:
            time_elem = article_element.select_one(selector)
            if time_elem:
                # Try to get datetime attribute first
                datetime_attr = time_elem.get('datetime')
                if datetime_attr:
                    return datetime_attr
                
                # Otherwise get text content
                time_text = time_elem.get_text().strip()
                if time_text:
                    return time_text
        
        # If no timestamp found, use current time
        return now_se().isoformat()
    
    def _extract_image(self, article_element) -> Optional[str]:
        """Extract image URL from article element."""
        # Try to find image
        img_elem = article_element.find('img')
        if img_elem:
            src = img_elem.get('src') or img_elem.get('data-src')
            if src:
                if src.startswith('/'):
                    return urljoin(self.base_url, src)
                elif not src.startswith('http'):
                    return urljoin(self.base_url, '/' + src)
                else:
                    return src
        
        return None
    
    def _deduplicate_news(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate news items based on URL and title similarity."""
        seen_urls = set()
        seen_titles = set()
        unique_news = []
        
        for item in news_items:
            url = item.get('url', '')
            title = item.get('title', '').lower()
            
            # Skip if URL already seen
            if url in seen_urls:
                continue
            
            # Skip if title is very similar (fuzzy matching)
            title_similar = False
            for seen_title in seen_titles:
                if self._titles_similar(title, seen_title):
                    title_similar = True
                    break
            
            if title_similar:
                continue
            
            # Add to unique items
            seen_urls.add(url)
            seen_titles.add(title)
            unique_news.append(item)
        
        return unique_news
    
    def _titles_similar(self, title1: str, title2: str, threshold: float = 0.8) -> bool:
        """Check if two titles are similar using simple similarity."""
        # Simple similarity check - can be improved with fuzzy matching
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if not words1 or not words2:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union)
        return similarity > threshold
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()


# Global instance
di_main_scraper = DIMainScraper()


def get_di_main_scraper() -> DIMainScraper:
    """Get the global DI main scraper instance."""
    return di_main_scraper 