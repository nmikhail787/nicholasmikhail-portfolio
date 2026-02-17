"""
Main scraper pipeline orchestrating all components.
"""
import logging
from typing import Dict

from .crawler import Crawler
from .extractor import ContentExtractor
from .enricher import DocumentEnricher
from .storage import DocumentStore

logger = logging.getLogger(__name__)


class ScraperPipeline:
    """
    Complete scraping pipeline from crawling to storage.
    """
    
    def __init__(
        self,
        start_url: str,
        output_path: str,
        max_pages: int = 100,
        max_depth: int = 3,
        delay: float = 1.0
    ):
        """
        Initialize the scraper pipeline.
        
        Args:
            start_url: The seed URL to start crawling
            output_path: Path to save the output JSONL file
            max_pages: Maximum number of pages to scrape
            max_depth: Maximum crawl depth
            delay: Delay between requests in seconds
        """
        self.start_url = start_url
        self.output_path = output_path
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.delay = delay
        
        # Initialize components
        self.crawler = Crawler(
            start_url=start_url,
            max_pages=max_pages,
            max_depth=max_depth,
            delay=delay
        )
        self.extractor = ContentExtractor()
        self.enricher = DocumentEnricher()
        
        # Statistics
        self.stats = {
            'pages_crawled': 0,
            'pages_extracted': 0,
            'pages_stored': 0,
            'pages_failed': 0
        }
    
    def run(self):
        """Run the complete scraping pipeline."""
        logger.info(f"Starting scraper pipeline for: {self.start_url}")
        logger.info(f"Output: {self.output_path}")
        logger.info(f"Max pages: {self.max_pages}, Max depth: {self.max_depth}")
        
        with DocumentStore(self.output_path) as store:
            # Crawl pages
            for url, html in self.crawler.crawl():
                self.stats['pages_crawled'] += 1
                
                # Extract content
                extracted = self.extractor.extract(html, url)
                if extracted is None:
                    logger.warning(f"Failed to extract content from: {url}")
                    self.stats['pages_failed'] += 1
                    continue
                
                self.stats['pages_extracted'] += 1
                
                # Enrich with metadata
                try:
                    document = self.enricher.enrich(
                        url=url,
                        title=extracted['title'],
                        body_text=extracted['body_text'],
                        categories=extracted['categories'],
                        sections=extracted['sections'],
                        references_count=extracted['references_count'],
                        links_count=extracted['links_count'],
                        has_code=extracted['has_code']
                    )
                    
                    # Store document
                    if store.add_document(document):
                        self.stats['pages_stored'] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to enrich/store document {url}: {e}")
                    self.stats['pages_failed'] += 1
        
        # Final statistics
        self._log_final_stats()
    
    def _log_final_stats(self):
        """Log final statistics."""
        logger.info("=" * 60)
        logger.info("SCRAPING COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Pages crawled:   {self.stats['pages_crawled']}")
        logger.info(f"Pages extracted: {self.stats['pages_extracted']}")
        logger.info(f"Pages stored:    {self.stats['pages_stored']}")
        logger.info(f"Pages failed:    {self.stats['pages_failed']}")
        logger.info(f"Output file:     {self.output_path}")
        logger.info("=" * 60)
    
    def get_stats(self) -> Dict:
        """Get pipeline statistics."""
        return self.stats.copy()