"""Test enricher"""
import requests
from src.extractor import ContentExtractor
from src.enricher import DocumentEnricher

# Fetch and extract
url = "https://en.wikipedia.org/wiki/Machine_learning"
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
html = response.text

extractor = ContentExtractor()
extracted = extractor.extract(html, url)

if extracted:
    # Enrich
    enricher = DocumentEnricher()
    document = enricher.enrich(
        url=url,
        title=extracted['title'],
        body_text=extracted['body_text'],
        categories=extracted['categories'],
        sections=extracted['sections'],
        references_count=extracted['references_count'],
        links_count=extracted['links_count'],
        has_code=extracted['has_code']
    )
    
    print("✅ ENRICHMENT SUCCESSFUL!")
    print(f"\nDocument structure:")
    print(f"  URL: {document['url']}")
    print(f"  Title: {document['title']}")
    print(f"  Fetched: {document['fetched_at']}")
    print(f"\nMetadata:")
    for key, value in document['metadata'].items():
        if isinstance(value, list):
            print(f"  {key}: {len(value)} items")
        else:
            print(f"  {key}: {value}")