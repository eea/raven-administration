import psycopg2
import os
import sys
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '../.env'))


def is_job_enabled():
    """Check if the aggregation cron job is enabled via environment variables"""
    enabled = os.environ.get('CRON_AGGREGATION_ENABLED', 'false').lower()
    return enabled in ('true', '1', 'yes', 'on')


# Check if the job is enabled
if not is_job_enabled():
    print("Aggregation cron job is disabled via CRON_AGGREGATION_ENABLED environment variable. Exiting.")
    sys.exit(0)

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
