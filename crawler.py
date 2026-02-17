"""
Web crawler for discovering and fetching pages.
"""
import time
import logging
from typing import Set, Optional, Dict
from urllib.parse import urljoin, urlparse
from collections import deque

import requests

from .config import (
    DEFAULT_DELAY, DEFAULT_TIMEOUT, USER_AGENT,
    SKIP_PATTERNS
)

logger = logging.getLogger(__name__)


class Crawler:
    """
    A web crawler that discovers and fetches pages from Wikipedia.
    """
    
    def __init__(
        self,
        start_url: str,
        max_pages: int = 100,
        max_depth: int = 3,
        delay: float = DEFAULT_DELAY,
        timeout: int = DEFAULT_TIMEOUT
    ):
        """
        Initialize the crawler.
        
        Args:
            start_url: The seed URL to start crawling from
            max_pages: Maximum number of pages to crawl
            max_depth: Maximum depth from start URL to crawl
            delay: Delay in seconds between requests
            timeout: Request timeout in seconds
        """
        self.start_url = start_url
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.delay = delay
        self.timeout = timeout
        
        # Parse the domain from start URL
        parsed = urlparse(start_url)
        self.domain = f"{parsed.scheme}://{parsed.netloc}"
        self.base_domain = parsed.netloc
        
        # Tracking
        self.visited: Set[str] = set()
        self.to_visit: deque = deque([(start_url, 0)])  # (url, depth)
        self.failed: Dict[str, str] = {}
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT
        })
        
        logger.info(f"Crawler initialized for domain: {self.base_domain}")
    
    def should_skip_url(self, url: str) -> bool:
        """Check if a URL should be skipped based on patterns."""
        url_lower = url.lower()
        return any(pattern.lower() in url_lower for pattern in SKIP_PATTERNS)
    
    def is_valid_url(self, url: str) -> bool:
        """Check if a URL is valid for crawling."""
        try:
            parsed = urlparse(url)
            
            # Must be HTTP/HTTPS
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Must be same domain
            if parsed.netloc != self.base_domain:
                return False
            
            # Check skip patterns
            if self.should_skip_url(url):
                return False
            
            return True
        except Exception:
            return False
    
    def normalize_url(self, url: str) -> str:
        """Normalize a URL by removing fragments."""
        parsed = urlparse(url)
        # Remove fragment
        url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            url += f"?{parsed.query}"
        return url
    
    def extract_links(self, html: str, current_url: str) -> Set[str]:
        """Extract valid internal links from HTML."""
        from bs4 import BeautifulSoup
        
        links = set()
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Wikipedia: look for links in content area
            content_div = soup.find('div', id='mw-content-text')
            if content_div:
                for anchor in content_div.find_all('a', href=True):
                    href = anchor['href']
                    
                    # Skip if it's a special page or has colon
                    if ':' in href:
                        continue
                    
                    # Convert to absolute URL
                    absolute_url = urljoin(current_url, href)
                    # Normalize
                    normalized_url = self.normalize_url(absolute_url)
                    # Validate
                    if self.is_valid_url(normalized_url):
                        links.add(normalized_url)
        except Exception as e:
            logger.warning(f"Error extracting links from {current_url}: {e}")
        
        return links
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a single page."""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=self.timeout)
            
            # Check status code
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                logger.warning(f"Skipping non-HTML content: {url}")
                return None
            
            return response.text
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching {url}")
            self.failed[url] = "Timeout"
            return None
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching {url}: {e}")
            self.failed[url] = f"HTTP {e.response.status_code}"
            return None
            
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            self.failed[url] = str(e)
            return None
    
    def crawl(self):
        """
        Crawl the website and yield (url, html) tuples.
        
        Yields:
            Tuple of (url, html_content)
        """
        page_count = 0
        
        while self.to_visit and page_count < self.max_pages:
            url, depth = self.to_visit.popleft()
            
            # Skip if already visited
            if url in self.visited:
                continue
            
            # Mark as visited
            self.visited.add(url)
            
            # Fetch the page
            html = self.fetch_page(url)
            
            if html is None:
                continue
            
            # Yield the page
            yield url, html
            page_count += 1
            
            # Extract and queue links if within depth limit
            if depth < self.max_depth:
                links = self.extract_links(html, url)
                for link in links:
                    if link not in self.visited:
                        self.to_visit.append((link, depth + 1))
            
            # Throttle requests
            if self.to_visit:
                time.sleep(self.delay)
        
        logger.info(f"Crawling complete. Visited {page_count} pages.")
    
    def get_stats(self) -> Dict:
        """Get crawling statistics."""
        return {
            'visited_count': len(self.visited),
            'failed_count': len(self.failed),
            'queued_count': len(self.to_visit)
        }