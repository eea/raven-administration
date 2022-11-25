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

    conn = psycopg2.connect(Config.DB_URI)
    cursor = conn.cursor()

    o = {
        "username": user,
        "password": generate_password_hash(password),
        "createdby": "",
        "created": datetime.now(tz=None),
        "name": name
    }

    # add user
    sql_user = """
        insert into users (username, password, createdby, created, name,locked) values (%(username)s, %(password)s, %(createdby)s, %(created)s, %(name)s,true)
        returning "id"
    """
    cursor.execute(sql_user, o)
    userid = cursor.fetchone()

    # add group
    sql_group = """
        insert into "group" ("name", "management", "data", "exporting", "processing", "qualitycontrol", "users", "allnetworks") 
        values ('admin', true, true, true, true, true, true, true)
        returning "id"
    """
    cursor.execute(sql_group, o)
    groupid = cursor.fetchone()

    # connect user and group
    cursor.execute("insert into usergroup (groupid, userid) values (%(groupid)s, %(userid)s)", {"groupid": groupid, "userid": userid})
    cursor.close()
    conn.commit()
    print("Admin added")

except Exception as err:
    print(str(err))
