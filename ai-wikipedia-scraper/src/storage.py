"""
Storage and output management.
"""
import json
import logging
import os
from typing import Set, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentStore:
    """
    Manages storage of scraped documents.
    """
    
    def __init__(self, output_path: str):
        """
        Initialize the document store.
        
        Args:
            output_path: Path to the output file (should end in .jsonl)
        """
        self.output_path = output_path
        self.seen_urls: Set[str] = set()
        self.document_count = 0
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize file (truncate if exists)
        self.file_handle = open(output_path, 'w', encoding='utf-8')
        logger.info(f"Initialized output file: {output_path}")
    
    def add_document(self, document: Dict) -> bool:
        """
        Add a document to the store.
        Implements idempotency by checking for duplicate URLs.
        
        Args:
            document: The document to store
            
        Returns:
            True if document was added, False if it was a duplicate
        """
        url = document.get('url')
        
        # Check for duplicate
        if url in self.seen_urls:
            logger.warning(f"Duplicate URL detected, skipping: {url}")
            return False
        
        try:
            # Write as JSONL
            json_line = json.dumps(document, ensure_ascii=False)
            self.file_handle.write(json_line + '\n')
            self.file_handle.flush()  # Ensure data is written
            
            # Track
            self.seen_urls.add(url)
            self.document_count += 1
            
            logger.info(f"Stored document {self.document_count}: {url}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing document {url}: {e}")
            return False
    
    def close(self):
        """Close the output file."""
        if hasattr(self, 'file_handle') and self.file_handle:
            self.file_handle.close()
            logger.info(f"Closed output file. Total documents: {self.document_count}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def get_stats(self) -> Dict[str, int]:
        """Get storage statistics."""
        return {
            'document_count': self.document_count,
            'unique_urls': len(self.seen_urls)
        }