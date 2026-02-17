"""
Content extraction and cleaning from HTML.
"""
import re
import logging
from typing import Optional, List, Dict
from bs4 import BeautifulSoup

from .config import MIN_CONTENT_LENGTH, MAX_CONTENT_LENGTH

logger = logging.getLogger(__name__)


class ContentExtractor:
    """
    Extracts and cleans content from Wikipedia pages.
    """
    
    def __init__(self):
        """Initialize the content extractor."""
        pass
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract the page title."""
        # Wikipedia puts title in <h1 class="firstHeading">
        title_tag = soup.find('h1', class_='firstHeading')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Try id="firstHeading"
        title_tag = soup.find(id='firstHeading')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Fallback to <title> tag
        title_tag = soup.find('title')
        if title_tag:
            # Wikipedia format: "Title - Wikipedia"
            title = title_tag.get_text().strip()
            return title.replace(' - Wikipedia', '')
        
        return "Untitled"
    
    def _extract_categories(self, soup: BeautifulSoup) -> List[str]:
        """Extract Wikipedia categories."""
        categories = []
        # Categories are in div with id="mw-normal-catlinks"
        cat_div = soup.find('div', id='mw-normal-catlinks')
        if cat_div:
            cat_links = cat_div.find_all('a')
            for link in cat_links:
                title_attr = link.get('title', '')
                if title_attr.startswith('Category:'):
                    category = link.get_text().strip()
                    if category:
                        categories.append(category)
        return categories
    
    def _extract_sections(self, soup: BeautifulSoup) -> List[str]:
        """Extract section headings (H2)."""
        sections = []
        # Find all H2 tags
        for h2 in soup.find_all('h2'):
            # Try to find headline span
            headline = h2.find(class_='mw-headline')
            if headline:
                section_text = headline.get_text().strip()
            else:
                section_text = h2.get_text().strip()
            
            # Skip meta sections and clean up
            section_text = section_text.replace('[edit]', '').strip()
            if section_text and section_text not in ['Contents', 'References', 'External links', 
                                   'See also', 'Notes', 'Further reading', 'Bibliography']:
                sections.append(section_text)
        return sections
    
    def _count_references(self, soup: BeautifulSoup) -> int:
        """Count citation references."""
        # Wikipedia uses class="reference"
        references = soup.find_all('sup', class_='reference')
        return len(references)
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract the main article content."""
        # Find the main content area
        content_div = soup.find('div', id='mw-content-text')
        
        if not content_div:
            return ""
        
        # Find all paragraphs in the content
        paragraphs = content_div.find_all('p')
        
        text_parts = []
        for p in paragraphs:
            # Remove reference markers
            for sup in p.find_all('sup'):
                sup.decompose()
            
            # Get text
            p_text = p.get_text(separator=' ', strip=True)
            
            # Only include substantial paragraphs
            if p_text and len(p_text) > 20:
                text_parts.append(p_text)
        
        # Join paragraphs
        text = '\n\n'.join(text_parts)
        
        return self._clean_text(text)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Replace multiple spaces with single space
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Replace multiple newlines with double newline
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line)
        
        return text.strip()
    
    def _count_internal_links(self, soup: BeautifulSoup) -> int:
        """Count internal Wikipedia links."""
        count = 0
        content_div = soup.find('div', id='mw-content-text')
        if content_div:
            for link in content_div.find_all('a', href=True):
                href = link['href']
                # Internal Wikipedia links start with /wiki/
                if href.startswith('/wiki/') and ':' not in href:
                    count += 1
        return count
    
    def extract(self, html: str, url: str) -> Optional[Dict[str, any]]:
        """
        Extract structured content from Wikipedia HTML.
        
        Args:
            html: HTML content
            url: URL of the page
            
        Returns:
            Dictionary with extracted content, or None if extraction failed
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract components
            title = self._extract_title(soup)
            body_text = self._extract_main_content(soup)
            
            # Validate content length
            if len(body_text) < MIN_CONTENT_LENGTH:
                logger.warning(f"Content too short for {url}: {len(body_text)} chars")
                return None
            
            if len(body_text) > MAX_CONTENT_LENGTH:
                logger.warning(f"Content too long for {url}, truncating")
                body_text = body_text[:MAX_CONTENT_LENGTH]
            
            # Extract metadata
            categories = self._extract_categories(soup)
            sections = self._extract_sections(soup)
            references_count = self._count_references(soup)
            links_count = self._count_internal_links(soup)
            
            return {
                'title': title,
                'body_text': body_text,
                'categories': categories,
                'sections': sections,
                'references_count': references_count,
                'links_count': links_count,
                'has_code': False  # Wikipedia articles rarely have code
            }
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None