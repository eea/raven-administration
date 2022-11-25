from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
import sys
import getopt
import psycopg2
from config import Config

name = ""
user = ""
password = ""

try:
    opts, args = getopt.getopt(sys.argv[1:], "n:u:p:")
    for k, v in opts:
        if k == "-n":
            name = v
        if k == "-u":
            user = v
        if k == "-p":
            password = v

    if len(name) == 0 or len(user) == 0 or len(password) == 0:
        raise Exception("Error: name, user and password must be provided (-n -u -p)")

    sql = """
        insert into users (username, password, createdby, created, name,locked) values (%(username)s, %(password)s, %(createdby)s, %(created)s, %(name)s,true)
        returning "id"
    """
    o = {
        "username": user,
        "password": generate_password_hash(password),
        "createdby": "",
        "created": datetime.now(tz=None),
        "name": name
    }

    conn = psycopg2.connect(Config.DB_URI)
    cursor = conn.cursor()
    cursor.execute(sql, o)
    userid = cursor.fetchone()
    cursor.execute("insert into usergroup (groupid, userid) values (1, %(userid)s)", {"userid": userid})
    cursor.close()
    conn.commit()
    print("User added")

except Exception as err:
    print(str(err))
