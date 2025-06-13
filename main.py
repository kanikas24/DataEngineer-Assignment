import logging
from skift_scraper import scrape_skift_news
from scraper_phocuswire import scrape_phocuswire_news
from db import create_articles_table, insert_article, get_latest_articles
from datetime import datetime
from utils import format_relative_time
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


if __name__ == "__main__":
    try:
        create_articles_table() 
        logging.info("Database table 'articles' ensured.")

        # Scrape Skift news
        skift_url = "https://skift.com/news/"
        skift_source = "Skift"
        logging.info(f"Starting to scrape Skift news from {skift_url}...")
        skift_articles = scrape_skift_news(skift_url, skift_source)

        if skift_articles:
            logging.info(f"Found {len(skift_articles)} articles from {skift_url}. Storing in database...")
            for article in skift_articles:
                insert_article(article)
            logging.info("Skift articles stored successfully.")
        else:
            logging.info(f"No articles found from {skift_url}.")

        logging.info("-" * 50)

        phocuswire_url = "https://www.phocuswire.com/RSS/All-News"
        phocuswire_source = "Phocuswire"
        logging.info(f"Starting to scrape Phocuswire news from {phocuswire_url}...")
        phocuswire_articles = scrape_phocuswire_news(phocuswire_url, phocuswire_source)
        logging.info(f"phocuswire_articles' {phocuswire_articles}")
        if phocuswire_articles:
            logging.info(f"Found {len(phocuswire_articles)} articles from {phocuswire_url}. Storing in database...")
            for article in phocuswire_articles:
                insert_article(article)
            logging.info("Phocuswire articles stored successfully.")
        else:
            logging.info(f"No articles found from {phocuswire_url}.")

        logging.info("\n" + "=" * 50)
        logging.info("Top 5 Latest Articles (Sorted by Timestamp)")
        logging.info("=" * 50)
        latest_articles = get_latest_articles(limit=20)
        for article in latest_articles:
            logging.info(f"DB time: {article['time']} - Source: {article['source']}")
        if latest_articles:
            for i, article in enumerate(latest_articles):
               
                try:
                    article_time_dt = datetime.fromisoformat(article['time'])
                    formatted_time = format_relative_time(article_time_dt)
                except (TypeError, ValueError):
                    formatted_time = article['time'] 

                logging.info(f"{i+1}. Title: {article['title']}")
                logging.info(f"   Link: {article['link']}")
                logging.info(f"   Time: {formatted_time}") 
                logging.info(f"   Source: {article['source']}")
                logging.info("-" * 20)
        else:
            logging.info("No articles found in the database.")

    except Exception as e:
        logging.critical(f"An unhandled error occurred in main execution: {e}", exc_info=True)