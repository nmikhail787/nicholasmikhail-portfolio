# AI Scraper - Wikipedia Article Collection Pipeline

A production-quality web scraping pipeline designed to collect high-quality documents from Wikipedia for AI workflows (RAG, search, fine-tuning, analytics).

## Overview

This scraper demonstrates production-minded engineering practices including:
- Clean separation of concerns (crawler, extractor, enricher, storage)
- Robust error handling and logging
- Idempotent operations (no duplicates on re-runs)
- Rich metadata extraction for AI workflows
- Structured JSONL output

## Background & Motivation

This project demonstrates production-quality data pipeline engineering, building on experience from developing similar systems in production environments.

### Related Experience: Phabricator Test Case Automation

In a recent internship, I built an automated data collection and processing pipeline with parallel architecture:

**System Architecture:**
- **Frontend**: Chrome extension scraped Phabricator URLs and test documentation
- **Backend**: Azure Promptflow ChatFlow model extracted and reformatted test cases
- **Integration**: Seamless API connection between browser automation and ML processing
- **Impact**: 90%+ reduction in processing time, organization-wide deployment

**Engineering Challenges Solved:**
- Reliable web content extraction from dynamic pages
- Structuring unstructured test documentation
- Building robust automation that scaled across the organization
- Integrating user-facing tools with ML backend systems

### This Project: Applying the Same Principles

This Wikipedia scraper applies identical engineering patterns to a different domain:

| Phabricator Project | Wikipedia Scraper | Core Skill |
|---------------------|-------------------|------------|
| Chrome extension scraping | Python crawler | Web content extraction |
| Test case extraction | Article/metadata extraction | Structured data from HTML |
| ChatFlow formatting | Enrichment pipeline | Data transformation |
| API integration | Modular architecture | System integration |
| Production deployment | Production-ready code | Robust engineering |

**Key Insight:** Whether building test automation or AI data pipelines, the fundamental engineering is the same:
- Reliable extraction of unstructured web content
- Transforming raw data into structured, usable formats
- Building robust, automated systems that scale
- Integrating with downstream AI/ML workflows

This project shows I can rapidly apply these skills to new domains—exactly what Forward Deployed Engineers do when working with diverse customer requirements.

## Site Selection: Wikipedia

I chose **Wikipedia** for this project because:

### 1. Production Relevance
- Wikipedia is a canonical data source for RAG systems and knowledge bases
- Real-world AI systems (GPT training, enterprise search) use Wikipedia extensively
- Demonstrates working with a site people actually scrape for AI applications

### 2. Rich, Structured Metadata
Wikipedia provides valuable signals for AI workflows:
- **Categories**: Enable semantic filtering and classification
- **Sections**: Document structure for chunking strategies
- **References**: Quality indicators (well-cited = authoritative)
- **Internal links**: Network analysis and hub page identification

### 3. Engineering Pragmatism
- Stable HTML structure = reliable extraction
- Explicitly allows scraping (respects robots.txt)
- Fast, responsive servers
- Minimizes technical risk for time-constrained project

### 4. AI Workflow Alignment
The metadata I extract directly supports:
- **RAG systems**: Categories + sections enable precise retrieval
- **Fine-tuning**: Word count + language for dataset curation
- **Search ranking**: References count + link count as authority signals
- **Content filtering**: Content type classification (article vs biography)

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup
```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Scraping
```bash
# Scrape 50 pages starting from Machine Learning
python scraper.py --start-url https://en.wikipedia.org/wiki/Machine_learning --max-pages 50

# Custom configuration
python scraper.py \
  --start-url https://en.wikipedia.org/wiki/Artificial_intelligence \
  --max-pages 100 \
  --max-depth 3 \
  --delay 1.5 \
  --output output/my_collection.jsonl
```

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--start-url` | Seed URL to start crawling (required) | - |
| `--output` | Output file path | `output/scraped_data.jsonl` |
| `--max-pages` | Maximum pages to scrape | 50 |
| `--max-depth` | Maximum crawl depth | 3 |
| `--delay` | Delay between requests (seconds) | 1.0 |
| `--verbose` | Enable debug logging | False |

### Analyze Results
```bash
python analytics.py --input output/scraped_data.jsonl
```

## Data Schema

Each document follows this JSON structure:
```json
{
  "url": "https://en.wikipedia.org/wiki/Machine_learning",
  "title": "Machine learning",
  "body_text": "Clean article text with boilerplate removed...",
  "fetched_at": "2024-02-03T10:30:00Z",
  "metadata": {
    "word_count": 8687,
    "char_count": 58424,
    "language": "en",
    "content_type": "encyclopedia_article",
    "reading_time_minutes": 43.4,
    "has_code": false,
    "categories": ["Machine learning", "Artificial intelligence"],
    "sections": ["History", "Approaches", "Applications"],
    "references_count": 247,
    "links_count": 1453
  }
}
```

### Field Descriptions

| Field | Type | Purpose for AI Workflows |
|-------|------|--------------------------|
| `url` | string | Deduplication, source tracking, citation |
| `title` | string | Document identification, semantic search |
| `body_text` | string | Primary content for embeddings, training, RAG |
| `fetched_at` | ISO 8601 | Temporal filtering, freshness tracking |
| `word_count` | integer | Length-based filtering, chunking decisions |
| `char_count` | integer | Token estimation, context window planning |
| `language` | string | Language-specific processing pipelines |
| `content_type` | string | Content-based filtering (articles vs bios) |
| `reading_time_minutes` | float | UX estimation, content complexity signal |
| `has_code` | boolean | Technical vs general content classification |
| `categories` | array | Semantic tags for filtering and retrieval |
| `sections` | array | Document structure for section-based retrieval |
| `references_count` | integer | Quality/authority signal |
| `links_count` | integer | Hub page detection, importance scoring |

## Design Decisions

### 1. Content Extraction Strategy

**Approach**: Target main content area (`#mw-content-text`), then extract paragraphs

**Why this works**:
- Wikipedia has consistent structure across articles
- Paragraph-based extraction avoids navigation/sidebar content
- Removes boilerplate (infoboxes, navboxes, edit links)

**AI benefit**: Clean text → better embeddings and more accurate retrieval

### 2. Metadata Selection

Fields were chosen based on common AI use cases:

**For RAG Systems**:
- `categories` + `sections`: Enable filtered retrieval ("Find ML articles about neural networks")
- `word_count`: Helps select appropriately-sized chunks
- `content_type`: Route queries to relevant document types

**For Training/Fine-tuning**:
- `language`: Filter datasets by language
- `word_count`: Quality control (filter very short articles)
- `references_count`: Authority signal for weighted sampling

**For Search**:
- `title` + `sections`: Relevance scoring
- `links_count`: PageRank-style importance
- `reading_time`: Result diversity (mix of quick reads and deep dives)

### 3. Robustness Features

**Idempotency**: URL-based deduplication prevents duplicates
- Tracks seen URLs in memory during run
- Can be extended to load previous runs for cross-session dedup

**Error Handling**: Graceful degradation
- Network failures logged, don't crash pipeline
- Invalid pages skipped with warnings
- Failed extractions tracked in stats

**Throttling**: Respectful crawling
- Configurable delay between requests (default 1s)
- Respects same-domain constraint
- User-Agent identification

## Architecture
```
┌─────────────────────────────────────────────────────────┐
│                     scraper.py (CLI)                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              ScraperPipeline (Orchestrator)             │
└─┬────────┬──────────┬──────────┬────────────────────────┘
  │        │          │          │
  ▼        ▼          ▼          ▼
┌─────┐ ┌──────┐ ┌────────┐ ┌─────────┐
│Crawl│ │Extract│ │Enrich  │ │Storage  │
│     │ │       │ │        │ │         │
│URLs │→│HTML   │→│+Metadata│→│JSONL   │
└─────┘ └──────┘ └────────┘ └─────────┘
```

### Component Responsibilities

- **`crawler.py`**: URL discovery, fetching, link extraction, error handling
- **`extractor.py`**: HTML parsing, content cleaning, Wikipedia-specific extraction
- **`enricher.py`**: Metadata generation (word count, language, content type)
- **`storage.py`**: JSONL output, deduplication, validation
- **`pipeline.py`**: Orchestration, error handling, statistics
- **`config.py`**: Centralized configuration

## Testing
```bash
# Run unit tests
python tests/test_extractor.py
```

Tests cover:
- Content extraction logic
- Text cleaning
- Minimum content validation
- Category extraction

## Example Output

Running with default settings produces output like:
```
2024-02-03 14:40:42 - Crawler initialized for domain: en.wikipedia.org
2024-02-03 14:40:42 - Starting scraper pipeline
2024-02-03 14:40:42 - Fetching: https://en.wikipedia.org/wiki/Machine_learning
2024-02-03 14:40:42 - Stored document 1: Machine_learning
...
2024-02-03 14:40:56 - SCRAPING COMPLETE
2024-02-03 14:40:56 - Pages crawled: 25
2024-02-03 14:40:56 - Pages stored: 25
```

## Sample Results

The included sample output (`output/scraped_data.jsonl`) contains 25 Wikipedia articles:
- **70,942 total words** across all documents
- **Content mix**: 52% encyclopedia articles, 32% technical articles, 16% biographies
- **100% success rate**: All pages extracted and stored successfully
- **Rich metadata**: Average 10.8 references and 616 internal links per page

## Future Work

For a production system, I would enhance:

### 1. Scalability
- **Distributed crawling**: Use Celery/Ray for parallel fetching
- **Database backend**: PostgreSQL with JSONB for structured queries
- **Cloud storage**: S3/GCS for large collections
- **Incremental updates**: Only recrawl changed pages (check Last-Modified headers)

### 2. Quality & Monitoring
- **Content quality scoring**: ML-based quality classifier
- **Deduplication**: Content-based (not just URL) using MinHash/SimHash
- **Monitoring dashboard**: Grafana for crawl health, error rates
- **Alerting**: PagerDuty for crawl failures

### 3. Advanced Features
- **Image extraction**: Extract and store article images
- **Table parsing**: Structured data from Wikipedia tables
- **Citation network**: Build graph of article relationships
- **Multilingual support**: Crawl multiple Wikipedia languages

### 4. AI Pipeline Integration
- **Vector embedding generation**: Compute embeddings on write
- **Automatic chunking**: Split long articles for RAG
- **Index to vector DB**: Direct ingestion to Pinecone/Weaviate
- **Data versioning**: Track corpus changes over time (DVC/LakeFS)

### 5. Compliance & Ethics
- **Strict robots.txt**: Enforce via robotparser
- **Rate limiting**: Per-domain limits
- **PII redaction**: Remove personal information if scraping user content
- **GDPR compliance**: Data retention policies

## Project Structure
```
krew-application-project/
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration
│   ├── crawler.py         # Web crawling
│   ├── extractor.py       # Content extraction
│   ├── enricher.py        # Metadata generation
│   ├── storage.py         # JSONL output
│   └── pipeline.py        # Orchestration
├── tests/
│   ├── __init__.py
│   └── test_extractor.py  # Unit tests
├── output/
│   └── scraped_data.jsonl # Sample output (25 docs)
├── scraper.py            # CLI entry point
├── analytics.py          # Data analysis
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## License

MIT License - Free for any purpose.

## Author

Created as a take home assignment demonstrating production quality scraping for AI workflows, building on experience developing similar automated data pipelines in production environments.