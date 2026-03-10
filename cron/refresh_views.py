import psycopg2
import os
import sys
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '../.env'))


# Aggregation is always enabled - no need to check environment variable
try:
    conn = psycopg2.connect(os.environ.get('DB_URI'))
except Exception as e:
    print(f"I am unable to connect to the database: {e}")
    sys.exit(1)

with conn.cursor() as curs:

    try:
        # Run function to refresh materialized views
        print("Refreshing materialized views. This may take a while...")
        curs.execute("select raven_refresh_aggregates()")
        print("Done")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

conn.commit()
curs.close()
