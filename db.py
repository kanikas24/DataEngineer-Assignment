import sqlite3
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE_NAME = 'articles.db'

def connect_db():
    """Connects to the SQLite database."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row # This allows accessing columns by name
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        return None

def create_articles_table():
    """Creates the articles table if it doesn't exist, or recreates it if schema changes are needed."""
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            # Drop table if it exists to apply schema changes
            cursor.execute('DROP TABLE IF EXISTS articles')
            logging.info("Existing 'articles' table dropped (if it existed).")

            cursor.execute('''
                CREATE TABLE articles (
                    article_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    link TEXT NOT NULL,
                    time DATETIME, -- Changed to DATETIME
                    source TEXT NOT NULL
                )
            ''')
            conn.commit()
            logging.info("Articles table created/ensured with DATETIME for 'time' column.")
        except sqlite3.Error as e:
            logging.error(f"Error creating articles table: {e}")
        finally:
            conn.close()

def insert_article(article):
    """Inserts a single article into the database."""
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            # Directly use the 'time' value provided by the scraper, assuming it's already in a sortable format
            time_to_insert = article.get('time', None)

            cursor.execute('''
                INSERT INTO articles (article_id, title, link, time, source)
                VALUES (?, ?, ?, ?, ?)
            ''', (article['article_id'], article['title'], article['link'], time_to_insert, article['source']))
            conn.commit()
            logging.info(f"Article '{article['title']}' inserted successfully.")
        except sqlite3.IntegrityError:
            logging.warning(f"Article with ID {article['article_id']} already exists. Skipping.")
        except sqlite3.Error as e:
            logging.error(f"Error inserting article '{article['title']}': {e}")
        finally:
            conn.close()

def get_all_articles():
    """Retrieves all articles from the database."""
    conn = connect_db()
    articles = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM articles')
            articles = cursor.fetchall()
            logging.info("All articles retrieved successfully.")
        except sqlite3.Error as e:
            logging.error(f"Error retrieving all articles: {e}")
        finally:
            conn.close()
    return articles

def get_latest_articles(limit=10):
    """Retrieves the latest articles from the database, sorted by time."""
    conn = connect_db()
    articles = []
    if conn:
        try:
            cursor = conn.cursor()
            # Order by time in descending order to get the latest articles
            # Filter out articles where time is NULL (if parsing failed in scraper)
            cursor.execute("SELECT * FROM articles WHERE time IS NOT NULL ORDER BY time DESC LIMIT ?", (limit,))
            articles = cursor.fetchall()
            logging.info(f"Latest {limit} articles retrieved successfully.")
        except sqlite3.Error as e:
            logging.error(f"Error retrieving latest articles: {e}")
        finally:
            conn.close()
    return articles

if __name__ == "__main__":
    create_articles_table()
    logging.info(f"Database '{DATABASE_NAME}' and table 'articles' ensured.")

    # Example usage:
    # article1 = {
    #     'article_id': 'test_id_1',
    #     'title': 'Test Article 1',
    #     'link': 'http://example.com/test1',
    #     'time': '2025-06-12 10:00:00', # Example of a properly formatted time
    #     'source': 'ExampleSite'
    # }
    # insert_article(article1)

    # article2 = {
    #     'article_id': 'test_id_2',
    #     'title': 'Test Article 2',
    #     'link': 'http://example.com/test2',
    #     'time': '2025-06-12 11:00:00', # Example of a properly formatted time
    #     'source': 'ExampleSite'
    # }
    # insert_article(article2)

    # logging.info("\nAll articles in database:")
    # for row in get_all_articles():
    #     print(row)

    # logging.info("\nLatest articles:")
    # for row in get_latest_articles(limit=3):
    #     print(row)