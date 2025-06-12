import requests
from bs4 import BeautifulSoup
from db import create_articles_table, insert_article
import logging
import time
from utils import parse_relative_time, generate_article_id

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def scrape_skift_news(url, source):
  
    response = None
    for i in range(3): 
        try:
            response = requests.get(url, timeout=10) 
            response.raise_for_status()  
            break # Success
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
        soup = BeautifulSoup(response.text, 'html.parser')

        heading_tags = soup.find_all(['h2', 'h3'])

        for heading in heading_tags:
            link_tag = heading.find('a')
            
            if link_tag and 'href' in link_tag.attrs:
                title = link_tag.get_text(strip=True)
                link = link_tag['href']
                
               
                time_element = None
                
                current_element = heading
                for _ in range(5): 
                    if current_element:
                        time_element = current_element.find('time')
                        if time_element:
                            break
                        current_element = current_element.parent
                
               
                if not time_element and heading.parent:
                    for sibling in heading.parent.find_next_siblings():
                        time_element = sibling.find('time')
                        if time_element:
                            break
                
                raw_time = time_element.get_text(strip=True) if time_element else 'No Time Found'
                
                parsed_time = parse_relative_time(raw_time)
                cleaned_time = parsed_time.isoformat() if parsed_time else raw_time 

                article_id = generate_article_id(link)

                articles_data.append({
                    'article_id': article_id,
                    'title': title,
                    'link': link,
                    'time': cleaned_time,
                    'source': source 
                })
    except Exception as e:
        logging.error(f"Error parsing HTML for {url}: {e}")
        return []
    
    return articles_data

