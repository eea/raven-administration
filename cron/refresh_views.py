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

# The same lock as the Pre aggregation page's update button
# (api/endpoints/misc/preaggregation/routes.py REFRESH_LOCK), so the two never refresh at
# once. Transaction-scoped: released by the commit below.
REFRESH_LOCK = 4502025

with conn.cursor() as curs:

    try:
        curs.execute("select pg_try_advisory_xact_lock(%s)", (REFRESH_LOCK,))
        if not curs.fetchone()[0]:
            print("A refresh is already running (started from the Pre aggregation page). Skipped.")
        else:
            # Run function to refresh materialized views
            print("Refreshing materialized views. This may take a while...")
            curs.execute("select raven_refresh_aggregates()")
            print("Done")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

conn.commit()
curs.close()
