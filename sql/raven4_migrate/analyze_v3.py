"""
Analyze Raven3 database for migration planning
"""
import os
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Source DB (Raven3)
SOURCE_DB = {
    'host': os.getenv('SOURCE_DB_HOST', 'localhost'),
    'port': int(os.getenv('SOURCE_DB_PORT', '5432')),
    'database': os.getenv('SOURCE_DB_NAME', 'ravendb'),
    'user': os.getenv('SOURCE_DB_USER', 'ravendb'),
    'password': os.getenv('SOURCE_DB_PASSWORD')
}

conn = psycopg2.connect(**SOURCE_DB)
cur = conn.cursor()

# List tables with row counts
cur.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    ORDER BY table_name
""")
tables = [r[0] for r in cur.fetchall()]

print('Raven3 tables with data:')
print('-' * 50)
for t in tables:
    try:
        cur.execute(f'SELECT COUNT(*) FROM "{t}"')
        count = cur.fetchone()[0]
        if count > 0:
            print(f'  {t}: {count:,} rows')
    except Exception as e:
        print(f'  {t}: ERROR - {e}')

conn.close()
