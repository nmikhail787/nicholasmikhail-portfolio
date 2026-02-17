"""
Document enrichment with AI-useful metadata.
"""
import re
import logging
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentEnricher:
    """
    Enriches documents with metadata useful for AI workflows.
    """
    
    # Common words for language detection
    ENGLISH_WORDS = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have',
        'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you',
        'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we'
    }
    
    def __init__(self):
        """Initialize the enricher."""
        pass
    
    def _count_words(self, text: str) -> int:
        """Count words in text."""
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    
    def _detect_language(self, text: str) -> str:
        """Detect language using simple heuristics."""
        # Extract words
        words = re.findall(r'\b\w+\b', text.lower())
        
        if len(words) < 10:
            return 'unknown'
        
        # Sample first 500 words for better detection
        sample = set(words[:500])
        
        # Count English word matches
        en_matches = len(sample & self.ENGLISH_WORDS)
        
        # If more than 20% are common English words, it's English
        if en_matches >= 5:  # At least 5 common words found
            return 'en'
        
        return 'unknown'
    
    def _classify_content_type(self, url: str, categories: list) -> str:
        """Classify content type based on URL and categories."""
        url_lower = url.lower()
        
        # Wikipedia-specific classification
        if 'list_of' in url_lower or 'List of' in url:
            return 'list_page'
        
        # Check categories
        category_str = ' '.join(categories).lower()
        
        if any(term in category_str for term in ['biography', 'people', 'person']):
            return 'biography'
        
        if any(term in category_str for term in ['technology', 'computer', 'software']):
            return 'technical_article'
        
        # Default for Wikipedia
        return 'encyclopedia_article'
    
    def _calculate_reading_time(self, word_count: int) -> float:
        """Calculate estimated reading time in minutes."""
        WORDS_PER_MINUTE = 200
        minutes = word_count / WORDS_PER_MINUTE
        return round(minutes, 1)
    
    def enrich(
        self,
        url: str,
        title: str,
        body_text: str,
        categories: list,
        sections: list,
        references_count: int,
        links_count: int,
        has_code: bool
    ) -> Dict[str, any]:
        """
        Enrich a document with AI-useful metadata.
        
        Args:
            url: Page URL
            title: Page title
            body_text: Main content text
            categories: List of categories
            sections: List of section headings
            references_count: Number of references
            links_count: Number of internal links
            has_code: Whether page contains code
            
        Returns:
            Complete enriched document
        """
        try:
            # Count metrics
            word_count = self._count_words(body_text)
            char_count = len(body_text)
            
            # Detect language
            language = self._detect_language(body_text)
            
            # Classify content
            content_type = self._classify_content_type(url, categories)
            
            # Calculate reading time
            reading_time = self._calculate_reading_time(word_count)
            
            # Timestamp
            fetched_at = datetime.utcnow().isoformat() + 'Z'
            
            # Build the document
            document = {
                'url': url,
                'title': title,
                'body_text': body_text,
                'fetched_at': fetched_at,
                'metadata': {
                    'word_count': word_count,
                    'char_count': char_count,
                    'language': language,
                    'content_type': content_type,
                    'reading_time_minutes': reading_time,
                    'has_code': has_code,
                    'categories': categories,
                    'sections': sections,
                    'references_count': references_count,
                    'links_count': links_count
                }
            }
            
            return document
            
        except Exception as e:
            logger.error(f"Error enriching document for {url}: {e}")
            raise