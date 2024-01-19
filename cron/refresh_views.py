import psycopg2
import os
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '../.env'))

try:
    conn = psycopg2.connect(os.environ.get('DB_URI'))
except:
    print("I am unable to connect to the database")

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
