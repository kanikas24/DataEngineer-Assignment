import requests
from bs4 import BeautifulSoup
import hashlib
import re
from datetime import datetime
from db import create_articles_table, insert_article
import logging
import time
from utils import generate_article_id, format_relative_time, parse_relative_time
try:
    import lxml
    PARSER = 'lxml'
except ImportError:
    logging.warning("lxml parser not found, falling back to built-in XML parser")
    PARSER = 'xml'

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def scrape_phocuswire_news(url, source):
    response = None
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    for i in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            break
        except requests.exceptions.Timeout:
            logging.warning(f"Timeout error fetching URL {url}. Retrying ({i+1}/3)...")
            time.sleep(2 ** i)
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching URL {url}: {e}")
            return []

    if not response:
        logging.error(f"Failed to fetch URL {url} after multiple retries.")
        return []

    articles_data = []

    try:
        soup = BeautifulSoup(response.text, PARSER)
        for item in soup.find_all('item'):
            title = item.title.text.strip() if item.title else None
            link = (item.link.text.strip() if item.link and item.link.text 
                    else item.guid.text.strip() if item.guid else None)

            pub_date_tag = item.find("pubDate") or item.find("pubdate")
            pub_date = pub_date_tag.text.strip() if pub_date_tag else 'No Time Found'
            logging.debug(f"Raw pubDate: {pub_date}")

            parsed_time = None
            if pub_date and pub_date != 'No Time Found':
                date_formats = [
                    "%a, %d %b %Y %H:%M:%S %z",
                    "%a, %d %b %Y %H:%M:%S %Z",
                    "%Y-%m-%dT%H:%M:%S%z",
                    "%Y-%m-%d %H:%M:%S",
                    "%d %b %Y %H:%M:%S %z"
                ]
                for fmt in date_formats:
                    try:
                        parsed_time = datetime.strptime(pub_date, fmt)
                        break
                    except ValueError:
                        continue
                if not parsed_time:
                    logging.warning(f"Could not parse date string: {pub_date}")
                    parsed_time = parse_relative_time(pub_date)

            cleaned_time = format_relative_time(parsed_time) if parsed_time else pub_date

            if not title or not link.strip() or link == 'No Link' or 'No Time Found' in cleaned_time:
                continue

            article_id = generate_article_id(link)
            article_data = {
                'article_id': article_id,
                'title': title,
                'link': link,
                'time': parsed_time.isoformat() if parsed_time else pub_date,
                'source': source
            }
            articles_data.append(article_data)
            logging.info(f"Added article: {title} ({cleaned_time})")

    except Exception as e:
        logging.error(f"Error parsing RSS feed for {url}: {e}")
        return []

    if not articles_data:
        logging.warning("No valid articles found in RSS feed")
    else:
        logging.info(f"Found {len(articles_data)} valid articles in RSS feed")
    return articles_data
