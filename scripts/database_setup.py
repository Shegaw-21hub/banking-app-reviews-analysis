import oracledb as cx_Oracle
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_oracle_client():
    """Configure Oracle client environment"""
    try:
        os.environ['TNS_ADMIN'] = r'C:\app\Shagiz\product\21c\homes\OraDB21Home1\network\admin'
        cx_Oracle.init_oracle_client()
        return True
    except Exception as e:
        logger.error(f"Oracle client setup failed: {e}")
        return False

def create_connection():
    """Create connection using your verified credentials"""
    load_dotenv()
    try:
        connection = cx_Oracle.connect(
            user=os.getenv('ORACLE_USER', 'DEMOUSER'),
            password=os.getenv('ORACLE_PASSWORD', 'demouser'),
            dsn="localhost:1521/XEPDB1"
        )
        logger.info("Successfully connected to Oracle XEPDB1")
        return connection
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        logger.error(f"Connection failed: ORA-{error.code}: {error.message}")
        return None

def table_exists(cursor, table_name):
    """Check if a table exists in the current schema"""
    cursor.execute("""
        SELECT COUNT(*) FROM user_tables WHERE table_name = :table_name
    """, [table_name.upper()])
    return cursor.fetchone()[0] > 0

def create_tables(connection):
    """Create the required tables if they don't already exist"""
    try:
        with connection.cursor() as cursor:
            # BANKS
            if not table_exists(cursor, 'BANKS'):
                cursor.execute("""
                CREATE TABLE banks (
                    bank_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    bank_name VARCHAR2(100) NOT NULL,
                    app_name VARCHAR2(100),
                    play_store_url VARCHAR2(255)
                )
                """)
                logger.info("Created table: BANKS")
            else:
                logger.info("Table already exists: BANKS")

            # REVIEWS
            if not table_exists(cursor, 'REVIEWS'):
                cursor.execute("""
                CREATE TABLE reviews (
                    review_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    bank_id NUMBER REFERENCES banks(bank_id),
                    review_text CLOB NOT NULL,
                    cleaned_review CLOB,
                    rating NUMBER(1) NOT NULL,
                    review_date DATE NOT NULL,
                    source VARCHAR2(50) DEFAULT 'Google Play',
                    sentiment VARCHAR2(10),
                    sentiment_score NUMBER(3,2),
                    CONSTRAINT chk_rating CHECK (rating BETWEEN 1 AND 5),
                    CONSTRAINT chk_sentiment CHECK (sentiment IN ('POSITIVE', 'NEGATIVE', 'NEUTRAL'))
                )
                """)
                logger.info("Created table: REVIEWS")
            else:
                logger.info("Table already exists: REVIEWS")

            # THEMES
            if not table_exists(cursor, 'THEMES'):
                cursor.execute("""
                CREATE TABLE themes (
                    theme_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    review_id NUMBER REFERENCES reviews(review_id),
                    theme_name VARCHAR2(50) NOT NULL,
                    keywords CLOB
                )
                """)
                logger.info("Created table: THEMES")
            else:
                logger.info("Table already exists: THEMES")

            connection.commit()
            return True

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        logger.error(f"Table creation failed: ORA-{error.code}: {error.message}")
        connection.rollback()
        return False

def main():
    if not setup_oracle_client():
        return

    connection = create_connection()
    if not connection:
        return

    try:
        if create_tables(connection):
            with connection.cursor() as cursor:
                cursor.execute("""
                SELECT table_name FROM user_tables 
                WHERE table_name IN ('BANKS', 'REVIEWS', 'THEMES')
                """)
                tables = [row[0] for row in cursor]
                print("\nCreated or confirmed tables:", ", ".join(tables))
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    main()
