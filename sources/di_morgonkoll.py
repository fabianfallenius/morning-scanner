#!/usr/bin/env python3
"""DI Morgonkoll news scraper for Morning Scanner."""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from common.utils_time import parse_iso_guess_tz
from common.ssl_config import get_ssl_config

logger = logging.getLogger(__name__)


class DIMorgonkollScraper:
    """Scrapes news from DI Morgonkoll."""
    
    def __init__(self):
        self.base_url = "https://www.di.se"
        self.morgonkoll_url = f"{self.base_url}/morgonkoll"
        self.session = None
        self.ssl_config = get_ssl_config()
        logger.info(f"DI Morgonkoll scraper initialized for {self.base_url}")
    
    async def _create_session(self) -> aiohttp.ClientSession:
        """Create aiohttp session with proper SSL configuration."""
        if self.session is None or self.session.closed:
            # Try strict SSL first, fallback to relaxed if needed
            try:
                ssl_context = self.ssl_config.get_aiohttp_ssl_context(strict=True)
                logger.info("Using strict SSL verification for DI.se")
            except Exception as e:
                logger.warning(f"Strict SSL failed, using relaxed: {e}")
                ssl_context = self.ssl_config.get_aiohttp_ssl_context(strict=False)
            
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
                    logger.info("DI.se robots.txt fetched successfully")
                    
                    # Check if we're allowed to scrape morgonkoll
                    if 'Disallow: /morgonkoll' in robots_content:
                        logger.warning("Robots.txt disallows morgonkoll scraping")
                        return False
                    else:
                        logger.info("Robots.txt allows morgonkoll scraping")
                        return True
                else:
                    logger.warning(f"Robots.txt returned status {response.status}")
                    return True  # Assume allowed if can't check
                    
        except Exception as e:
            logger.warning(f"Could not fetch robots.txt, proceeding with caution: {e}")
            return True  # Assume allowed if can't check
    
    async def _fetch_morgonkoll_page(self) -> Optional[str]:
        """Fetch the DI Morgonkoll page."""
        try:
            session = await self._create_session()
            logger.info(f"Fetching DI Morgonkoll: {self.morgonkoll_url}")
            
            async with session.get(self.morgonkoll_url) as response:
                if response.status == 200:
                    content = await response.text()
                    logger.info(f"Successfully fetched DI Morgonkoll page ({len(content)} chars)")
                    return content
                else:
                    logger.error(f"Failed to fetch DI Morgonkoll: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching DI Morgonkoll page: {e}")
            return None
    
    async def _parse_morgonkoll_content(self, html: str) -> List[Dict[str, Any]]:
        """Parse news items from DI Morgonkoll HTML content."""
        news_items = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for news items in DI Morgonkoll
            # Adjust selectors based on actual DI Morgonkoll structure
            news_selectors = [
                'article',
                '.news-item',
                '.morgonkoll-item',
                '.di-news',
                '[class*="news"]',
                '[class*="morgonkoll"]'
            ]
            
            news_elements = []
            for selector in news_selectors:
                news_elements = soup.select(selector)
                if news_elements:
                    logger.info(f"Found {len(news_elements)} news elements using selector: {selector}")
                    break
            
            # If no specific selectors found, try generic approach
            if not news_elements:
                # Look for any div with news-like content
                news_elements = soup.find_all('div', class_=lambda x: x and any(
                    keyword in x.lower() for keyword in ['nyhet', 'news', 'artikel', 'article', 'post']
                ))
                logger.info(f"Fallback: Found {len(news_elements)} news elements using generic approach")
            
            for element in news_elements[:15]:  # Limit to 15 items
                try:
                    news_item = await self._extract_news_item(element)
                    if news_item:
                        news_items.append(news_item)
                        
                except Exception as e:
                    logger.debug(f"Error extracting news item: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(news_items)} news items from DI Morgonkoll")
            
        except Exception as e:
            logger.error(f"Error parsing DI Morgonkoll content: {e}")
        
        return news_items
    
    async def _extract_news_item(self, element) -> Optional[Dict[str, Any]]:
        """Extract individual news item data from an element."""
        try:
            # Extract title
            title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'h5'])
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            if not title or len(title) < 10:
                return None
            
            # Extract link
            link_elem = element.find('a', href=True)
            if not link_elem:
                return None
            
            link = link_elem['href']
            if not link.startswith('http'):
                link = f"{self.base_url.rstrip('/')}/{link.lstrip('/')}"
            
            # Extract snippet/description
            snippet_elem = element.find(['p', 'div'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['excerpt', 'summary', 'description', 'text', 'lead']
            ))
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
            
            # Extract timestamp
            timestamp = await self._extract_timestamp(element)
            
            # Extract source/category if available
            source_elem = element.find(['span', 'div'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['source', 'category', 'section', 'rubrik']
            ))
            source = source_elem.get_text(strip=True) if source_elem else "DI Morgonkoll"
            
            news_item = {
                'title': title,
                'url': link,
                'snippet': snippet,
                'timestamp': timestamp,
                'source': source,
                'scraped_at': datetime.now().isoformat()
            }
            
            return news_item
            
        except Exception as e:
            logger.debug(f"Error extracting news item: {e}")
            return None
    
    async def _extract_timestamp(self, element) -> str:
        """Extract timestamp from element."""
        try:
            # Look for time element with datetime attribute
            time_elem = element.find('time', datetime=True)
            if time_elem:
                timestamp = time_elem.get('datetime')
                if timestamp:
                    try:
                        parsed_time = parse_iso_guess_tz(timestamp)
                        return parsed_time.isoformat()
                    except:
                        pass
            
            # Look for date/time in text
            date_selectors = [
                '.date', '.time', '.timestamp', '.published',
                '[class*="date"]', '[class*="time"]'
            ]
            
            for selector in date_selectors:
                date_elem = element.find(['span', 'div'], class_=selector)
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    if date_text:
                        try:
                            parsed_time = parse_iso_guess_tz(date_text)
                            return parsed_time.isoformat()
                        except:
                            pass
            
            # Fallback to current time
            return datetime.now().isoformat()
            
        except Exception as e:
            logger.debug(f"Error extracting timestamp: {e}")
            return datetime.now().isoformat()
    
    async def scrape_news(self) -> List[Dict[str, Any]]:
        """Scrape news from DI Morgonkoll."""
        logger.info("Starting DI Morgonkoll scraping")
        
        try:
            # Check robots.txt first
            robots_allowed = await self._check_robots_txt()
            if not robots_allowed:
                logger.warning("Robots.txt disallows scraping - aborting")
                return []
            
            # Fetch the morgonkoll page
            html_content = await self._fetch_morgonkoll_page()
            if not html_content:
                logger.error("Failed to fetch DI Morgonkoll page")
                return []
            
            # Parse the content
            news_items = await self._parse_morgonkoll_content(html_content)
            
            logger.info(f"DI Morgonkoll scraping completed: {len(news_items)} items found")
            return news_items
            
        except Exception as e:
            logger.error(f"Error during DI Morgonkoll scraping: {e}")
            return []
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None


# For backward compatibility
async def scrape():
    """Legacy scrape function."""
    scraper = DIMorgonkollScraper()
    try:
        return await scraper.scrape_news()
    finally:
        await scraper.close() 