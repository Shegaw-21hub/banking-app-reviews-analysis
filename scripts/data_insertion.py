import oracledb as cx_Oracle
import pandas as pd
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection parameters
ORACLE_USER = 'demouser'
ORACLE_PASSWORD = 'demouser'
ORACLE_DSN = 'localhost:1521/XEPDB1'

CSV_FILE_PATH = 'data/bank_reviews_clean.csv'

def connect_to_db():
    try:
        connection = cx_Oracle.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)
        logger.info("Connected to Oracle database.")
        return connection
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")
        return None

def insert_banks_and_get_ids(connection, df):
    cursor = connection.cursor()
    bank_names = df['bank'].dropna().unique()
    bank_id_map = {}

    try:
        for bank_name in bank_names:
            # Check if the bank already exists
            cursor.execute("SELECT bank_id FROM banks WHERE bank_name = :bank_name", {"bank_name": bank_name})
            result = cursor.fetchone()
            if result:
                bank_id = result[0]
            else:
                cursor.execute("""
                    INSERT INTO banks (bank_name, app_name, play_store_url)
                    VALUES (:bank_name, :app_name, :url)
                    RETURNING bank_id INTO :bank_id
                """, {
                    "bank_name": bank_name,
                    "app_name": bank_name,
                    "url": None,
                    "bank_id": cursor.var(cx_Oracle.NUMBER)
                })
                bank_id = int(cursor.getimplicitresults()[0][0])
            bank_id_map[bank_name] = bank_id

        connection.commit()
        logger.info("Banks inserted or found successfully.")
        return bank_id_map
    except Exception as e:
        logger.error(f"Error inserting banks: {e}")
        connection.rollback()
        return {}

def insert_reviews(connection, df, bank_id_map):
    cursor = connection.cursor()
    inserted_rows = 0

    for _, row in df.iterrows():
        bank_name = row.get('bank')
        if bank_name not in bank_id_map:
            logger.warning(f"Skipping row due to unknown bank: {bank_name}")
            continue

        try:
            rating = int(row.get('rating'))
        except (ValueError, TypeError):
            logger.warning(f"Skipping row due to invalid rating: {row.get('rating')}")
            continue

        try:
            cursor.execute("""
                INSERT INTO reviews 
                (bank_id, review_text, cleaned_review, rating, review_date, source)
                VALUES (:bank_id, :review_text, :cleaned_review, :rating, TO_DATE(:review_date, 'YYYY-MM-DD'), :source)
            """, {
                "bank_id": bank_id_map[bank_name],
                "review_text": row.get('review'),
                "cleaned_review": row.get('cleaned_review'),
                "rating": rating,
                "review_date": str(row.get('date')),
                "source": row.get('source', 'Google Play')
            })
            inserted_rows += 1
        except Exception as e:
            logger.warning(f"Skipping row due to error: {e}")

    connection.commit()
    logger.info(f"Inserted {inserted_rows} rows into reviews table.")

def main():
    if not os.path.isfile(CSV_FILE_PATH):
        logger.error(f"CSV file '{CSV_FILE_PATH}' not found.")
        return

    try:
        df = pd.read_csv(CSV_FILE_PATH)
    except Exception as e:
        logger.error(f"Failed to load CSV: {e}")
        return

    connection = connect_to_db()
    if not connection:
        return

    try:
        bank_id_map = insert_banks_and_get_ids(connection, df)
        if not bank_id_map:
            logger.error("No banks inserted or retrieved. Aborting review insertion.")
            return

        insert_reviews(connection, df, bank_id_map)
    finally:
        connection.close()
        logger.info("Database connection closed.")

if __name__ == "__main__":
    main()
