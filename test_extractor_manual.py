"""Quick manual test of extractor"""
import requests
from bs4 import BeautifulSoup
from src.extractor import ContentExtractor

# Fetch a sample Wikipedia page
url = "https://en.wikipedia.org/wiki/Machine_learning"
print(f"Fetching {url}...")
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
html = response.text

# Debug: Check raw extraction
soup = BeautifulSoup(html, 'html.parser')
content_div = soup.find('div', id='mw-content-text')
if content_div:
    paragraphs = content_div.find_all('p')
    print(f"Found {len(paragraphs)} paragraphs")
    
    # Show first few paragraphs
    for i, p in enumerate(paragraphs[:3]):
        p_text = p.get_text(strip=True)
        print(f"\nParagraph {i+1} ({len(p_text)} chars):")
        print(p_text[:200])

# Now try with extractor
print("\n" + "="*60)
print("Testing ContentExtractor...")
print("="*60)

extractor = ContentExtractor()
result = extractor.extract(html, url)

# Print results
if result:
    print("\n✅ EXTRACTION SUCCESSFUL!")
    print(f"Title: {result['title']}")
    print(f"Body length: {len(result['body_text'])} characters")
    print(f"Word count: ~{len(result['body_text'].split())} words")
    print(f"\nCategories ({len(result['categories'])}):")
    for cat in result['categories'][:5]:
        print(f"  - {cat}")
    print(f"\nSections ({len(result['sections'])}):")
    for sec in result['sections'][:5]:
        print(f"  - {sec}")
    print(f"\nReferences: {result['references_count']}")
    print(f"Internal links: {result['links_count']}")
    print(f"\nFirst 300 chars of body:")
    print("-"*60)
    print(result['body_text'][:300])
    print("-"*60)
else:
    print("❌ Extraction failed!")