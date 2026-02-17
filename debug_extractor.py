"""Debug script to see what we're getting"""
import requests
from bs4 import BeautifulSoup

url = "https://en.wikipedia.org/wiki/Machine_learning"
print(f"Fetching {url}...")
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
html = response.text

soup = BeautifulSoup(html, 'html.parser')

# Check for main content div
content_div = soup.find('div', id='mw-content-text')
print(f"\nFound content div: {content_div is not None}")

if content_div:
    # Try to get some text
    text = content_div.get_text()
    print(f"Content div has {len(text)} characters")
    print(f"First 500 chars:\n{text[:500]}")
else:
    print("No content div found!")
    
# Check what divs exist
print("\nAll divs with IDs:")
for div in soup.find_all('div', id=True)[:10]:
    print(f"  - {div.get('id')}")