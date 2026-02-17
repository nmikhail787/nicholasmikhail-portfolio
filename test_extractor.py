"""Tests for content extraction."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extractor import ContentExtractor


def test_extract_title():
    """Test title extraction."""
    extractor = ContentExtractor()
    
    # More realistic HTML with paragraphs
    html = '''
    <html>
    <head><title>Test Page - Wikipedia</title></head>
    <body>
        <div id="mw-content-text">
            <p>This is a test paragraph with enough content to pass the minimum length requirement. 
            It contains multiple sentences to ensure we have sufficient text for extraction.</p>
            <p>Here is another paragraph with additional content to make sure we exceed the minimum
            character count that is required for successful extraction.</p>
        </div>
    </body>
    </html>
    '''
    result = extractor.extract(html, 'http://example.com')
    assert result is not None
    assert 'Test Page' in result['title']
    assert len(result['body_text']) > 0


def test_clean_text():
    """Test text cleaning."""
    extractor = ContentExtractor()
    
    text = "This   has    multiple     spaces.\n\n\n\nAnd multiple newlines."
    cleaned = extractor._clean_text(text)
    
    # Check no multiple spaces
    assert '  ' not in cleaned
    # Check no more than 2 newlines in a row
    assert '\n\n\n' not in cleaned


def test_min_content_length():
    """Test minimum content length validation."""
    extractor = ContentExtractor()
    
    # Too short - should return None
    html = '''<html><body>
        <div id="mw-content-text"><p>Short</p></div>
    </body></html>'''
    result = extractor.extract(html, 'http://example.com')
    assert result is None
    
    # Long enough - should succeed
    html = '''<html><body>
        <div id="mw-content-text">
            <p>This is a much longer paragraph that should pass the minimum content length check.
            We need to include enough text here to ensure that the extraction succeeds and returns
            a valid result with all the expected fields populated correctly.</p>
        </div>
    </body></html>'''
    result = extractor.extract(html, 'http://example.com')
    assert result is not None


def test_extract_categories():
    """Test category extraction."""
    extractor = ContentExtractor()
    
    html = '''<html><body>
        <div id="mw-content-text">
            <p>Main content paragraph with sufficient length to pass validation checks.
            This paragraph contains enough text to meet the minimum requirements for extraction.
            We need to add more content here to ensure it exceeds the minimum character count.
            Additional sentences are included to make absolutely sure this passes the validation.</p>
        </div>
        <div id="mw-normal-catlinks">
            <a href="/wiki/Category:Test" title="Category:Test">Test</a>
            <a href="/wiki/Category:Example" title="Category:Example">Example</a>
        </div>
    </body></html>'''
    
    result = extractor.extract(html, 'http://example.com')
    assert result is not None
    assert len(result['categories']) == 2
    assert 'Test' in result['categories']
    assert 'Example' in result['categories']


if __name__ == '__main__':
    test_extract_title()
    print("✓ test_extract_title passed")
    
    test_clean_text()
    print("✓ test_clean_text passed")
    
    test_min_content_length()
    print("✓ test_min_content_length passed")
    
    test_extract_categories()
    print("✓ test_extract_categories passed")
    
    print("\n✅ All tests passed!")