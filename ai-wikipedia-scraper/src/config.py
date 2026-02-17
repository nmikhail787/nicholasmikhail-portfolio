"""
Configuration settings for the AI scraper.
"""
import os

# Scraping configuration
DEFAULT_MAX_PAGES = 50
DEFAULT_MAX_DEPTH = 3
DEFAULT_DELAY = 1.0  # seconds between requests
DEFAULT_TIMEOUT = 10  # seconds
USER_AGENT = "AI-Educational-Scraper/1.0 (Educational Purpose)"

# Content extraction settings
MIN_CONTENT_LENGTH = 200  # Minimum characters for valid content
MAX_CONTENT_LENGTH = 1000000  # Maximum to prevent memory issues

# Output
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")

# URL patterns to skip
SKIP_PATTERNS = {
    'Special:', 'Wikipedia:', 'Help:', 'Talk:', 'User:', 'Template:',
    'Category:', 'File:', 'Portal:', 'Book:',
    '.jpg', '.png', '.pdf', '.svg'
}