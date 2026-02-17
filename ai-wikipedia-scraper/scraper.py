#!/usr/bin/env python3
"""
Command-line interface for the AI scraper.
"""
import argparse
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import ScraperPipeline
from src.config import DEFAULT_MAX_PAGES, DEFAULT_MAX_DEPTH, DEFAULT_DELAY


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='AI Scraper - Scrape websites and prepare data for AI workflows',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape Machine Learning articles
  python scraper.py --start-url https://en.wikipedia.org/wiki/Machine_learning --max-pages 50
  
  # Scrape with custom settings
  python scraper.py --start-url https://en.wikipedia.org/wiki/Artificial_intelligence --max-pages 100 --max-depth 4
        """
    )
    
    parser.add_argument(
        '--start-url',
        required=True,
        help='The seed URL to start crawling from'
    )
    
    parser.add_argument(
        '--output',
        default='output/scraped_data.jsonl',
        help='Output file path (default: output/scraped_data.jsonl)'
    )
    
    parser.add_argument(
        '--max-pages',
        type=int,
        default=DEFAULT_MAX_PAGES,
        help=f'Maximum number of pages to scrape (default: {DEFAULT_MAX_PAGES})'
    )
    
    parser.add_argument(
        '--max-depth',
        type=int,
        default=DEFAULT_MAX_DEPTH,
        help=f'Maximum crawl depth (default: {DEFAULT_MAX_DEPTH})'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=DEFAULT_DELAY,
        help=f'Delay between requests in seconds (default: {DEFAULT_DELAY})'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Validate URL
    if not args.start_url.startswith(('http://', 'https://')):
        print(f"Error: Invalid URL. Must start with http:// or https://")
        sys.exit(1)
    
    # Run the scraper
    try:
        pipeline = ScraperPipeline(
            start_url=args.start_url,
            output_path=args.output,
            max_pages=args.max_pages,
            max_depth=args.max_depth,
            delay=args.delay
        )
        
        pipeline.run()
        
        print(f"\n✓ Scraping complete! Output saved to: {args.output}")
        
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        logging.exception("Fatal error in scraper")
        sys.exit(1)


if __name__ == '__main__':
    main()