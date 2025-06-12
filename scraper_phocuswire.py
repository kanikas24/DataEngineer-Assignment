import requests
from bs4 import BeautifulSoup
import hashlib
import re
from datetime import datetime
from db import create_articles_table, insert_article
import logging
import time
from utils import generate_article_id
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
            response = requests.get(url, headers=headers, timeout=10) # Add timeout

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
    # logging.info(f"hellodata {response.text}")


    articles_data = []
    try:
        soup = BeautifulSoup(response.text, 'lxml')  # Use best available XML parser
        for item in soup.find_all('item'):
            title = item.title.text.strip() if item.title else None
            link = (item.link.text.strip() if item.link and item.link.text 
               else item.guid.text.strip() if item.guid else None)
            pub_date = item.pubdate.text.strip() if item.pubdate else 'No Time Found'


            parsed_time = None
            try:
                # Parse RFC 822 format date (common in RSS feeds)
                parsed_time = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
            except ValueError:
                logging.warning(f"Could not parse date string: {pub_date}")

            cleaned_time = parsed_time.strftime('%Y-%m-%d %H:%M:%S') if parsed_time else pub_date

            if not title or not link.strip() or link == 'No Link' or 'No Time Found' in cleaned_time:
                continue
            logging.info(f"hellodata {articles_data}")

            article_id = generate_article_id(link)
            articles_data.append({
                'article_id': article_id,
                'title': title,
                'link': link,
                'time': cleaned_time,
                'source': source
            })
            logging.info(f'Article data - Title: {articles_data}')


    except Exception as e:
        logging.error(f"Error parsing RSS feed for {url}: {e}")
        return []
    
    if not articles_data:
        logging.warning("No valid articles found in RSS feed")
    else:
        logging.info(f"Found {len(articles_data)} valid articles in RSS feed")
    return articles_data

