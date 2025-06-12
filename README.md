# News Headlines Pipeline

A Python data pipeline that extracts latest news articles from Skift and PhocusWire, stores them in SQLite, and displays the top 5 most recent articles.

## Features

- **Skift Scraper**: Web scraping for Skift news articles
- **PhocusWire Parser**: RSS feed processing for PhocusWire articles
- **Incremental Loading**: Only fetches new articles based on timestamps
- **SQLite Storage**: Persistent storage of article data
- **Robust Error Handling**: Network retries, duplicate prevention

## Data Extraction Methods

### Skift (skift_scraper.py)
- Uses BeautifulSoup for HTML parsing
- Extracts:
  - Article titles from heading tags
  - URLs from anchor tags
  - Publication times from time elements
- Handles relative time strings (e.g. "2 hours ago")

### PhocusWire (scraper_phocuswire.py)
- Parses RSS feed
- Extracts:
  - Titles from item.title
  - URLs from item.link or item.guid
  - Publication dates from item.pubDate
- Supports multiple date formats

## Database Schema (db.py)

```sql
CREATE TABLE articles (
    article_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    time TEXT NOT NULL,
    source TEXT NOT NULL,
    UNIQUE(article_id)
)
```

- `article_id`: SHA-256 hash of URL
- `time`: ISO format timestamp
- `source`: "skift" or "phocuswire"

## Incremental Loading

- Articles are identified by URL hash
- Database enforces uniqueness
- Only new articles are inserted

## Error Handling

- Network request retries (3 attempts)
- Timeout handling
- Date parsing fallbacks
- Duplicate article prevention
- Comprehensive logging

## Requirements

- Python 3.8+
- Required packages:
  - beautifulsoup4
  - requests
  - lxml (recommended)

## Usage

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the pipeline:
```bash
python main.py
```

3. Output shows top 5 most recent articles:
```
1. [Skift] Article Title (2 hours ago)
2. [PhocusWire] Article Title (1 day ago)
...
```

## Project Structure

- `main.py`: Main execution script
- `skift_scraper.py`: Skift web scraper
- `scraper_phocuswire.py`: PhocusWire RSS parser
- `db.py`: Database operations
- `utils.py`: Helper functions
- `articles.db`: SQLite database