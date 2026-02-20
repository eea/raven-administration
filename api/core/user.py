from datetime import datetime
from core.database import CursorFromPool
from core.base_model import RavenBaseModel
from typing import List, Optional
from werkzeug.security import check_password_hash, generate_password_hash


class User(RavenBaseModel):
    id: str
    name: str
    username: str
    management: bool
    data: bool
    exporting: bool
    processing: bool
    qualitycontrol: bool
    users: bool
    allnetworks: bool
    networks: List[str]


# USER
def get_user(username, password):
    with CursorFromPool() as cursor:
        sql = """
          select
            u.id, u.name, u.username, u.password,
            bool_or(g.management) as management, 
            bool_or(g.data) as data,
            bool_or(g.exporting) as exporting,
            bool_or(g.processing) as processing, 
            bool_or(g.qualitycontrol) as qualitycontrol,
            bool_or(g.allnetworks) as allnetworks,
            bool_or(g.users) as users,
            CASE
                WHEN bool_or(g.allnetworks) = true
                THEN '{}'
                ELSE coalesce( array_agg(gn.networkid) FILTER (WHERE gn.networkid is not NULL),'{}')
            END as networks
          from users u, usergroup ug, "group" g left join groupnetwork gn on gn.groupid = g.id
          where ug.userid = u.id
          and ug.groupid = g.id
          and u.username = %(username)s
          group by u.id, u.name, u.username, u.password             
        """
        cursor.execute(sql, {"username": username})
        user = cursor.fetchone()

        if user == None or check_password_hash(user["password"], password) == False:
            return None

        return User(**user)


def get_claims(user: User):
    return {
        "name": user.name,
        "management": user.management,
        "data": user.data,
        "exporting": user.exporting,
        "processing": user.processing,
        "qualitycontrol": user.qualitycontrol,
        "allnetworks": user.allnetworks,
        "users": user.users,
        "networks": user.networks
    }


def remove_user(id):
    with CursorFromPool() as cursor:
        if is_locked_user(cursor, id):
            raise Exception("Cannot delete locked user")
        sql = "delete from users where id = %(id)s and locked = false"
        cursor.execute(sql, {"id": id})


def are_user_and_group_table_empty():
    with CursorFromPool() as cursor:
        cursor.execute("select 1 from users")
        if cursor.rowcount > 0:
            return False
        cursor.execute("""
          select 1 from "group"
        """)
        if cursor.rowcount > 0:
            return False
    return True


def add_admin(password):
    if not are_user_and_group_table_empty():
        raise Exception("User and group table are not empty")

    with CursorFromPool() as cursor:
        o = {
            "username": "admin",
            "password": generate_password_hash(password),
            "createdby": "",
            "created": datetime.now(tz=None),
            "name": "Administrator"
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
          insert into "group" ("name", "management", "data", "exporting", "processing", "qualitycontrol", "users", "allnetworks","locked") 
          values ('admin', true, true, true, true, true, true, true,true)
          returning "id"
      """
        cursor.execute(sql_group, o)
        groupid = cursor.fetchone()

        # connect user and group
        cursor.execute("insert into usergroup (groupid, userid) values (%(groupid)s, %(userid)s)", {"groupid": groupid["id"], "userid": userid["id"]})


def add_user(name, username, password, groups, createdby):
    if len(groups) == 0:
        raise Exception("Groups cannot be empty")

    with CursorFromPool() as cursor:
        sql = """
            insert into users (username, password, createdby, created, name) values (%(username)s, %(password)s, %(createdby)s, %(created)s, %(name)s)
            returning "id"
        """
        o = {
            "username": username,
            "password": generate_password_hash(password),
            "createdby": createdby,
            "created": datetime.now(tz=None),
            "name": name
        }
        cursor.execute(sql, o)
        userid = cursor.fetchone()

        sql = "insert into usergroup (groupid, userid) values (%(groupid)s, %(userid)s)"
        for g in groups:
            cursor.execute(sql, {"groupid": g, "userid": userid["id"]})


def update_user(id, name, username, password, groups, createdby):
    if len(groups) == 0:
        raise Exception("Groups cannot be empty")

    with CursorFromPool() as cursor:
        o = {
            "username": username,
            "createdby": createdby,
            "created": datetime.now(tz=None),
            "name": name,
            "id": id
        }

        sql = """update users set username=%(username)s, name=%(name)s, createdby=%(createdby)s, created=%(created)s where "id"=%(id)s"""
        if not (password == "" or password == None):
            o["password"] = generate_password_hash(password)
            sql = """update users set username=%(username)s, password=%(password)s, name=%(name)s, createdby=%(createdby)s, created=%(created)s where "id"=%(id)s"""

        cursor.execute(sql, o)

        if not is_locked_user(cursor, id):  # locked users cannot change group
            cursor.execute("delete from usergroup where userid = %(userid)s", {"userid": id})

            sql = "insert into usergroup (groupid, userid) values (%(groupid)s, %(userid)s)"
            for g in groups:
                cursor.execute(sql, {"groupid": g, "userid": id})


def is_locked_user(cursor, id):
    cursor.execute("select 1 from users where id = %(id)s and locked = true", {"id": id})
    return cursor.rowcount > 0


# GROUP
def add_group(name, management, data, exporting, processing, qualitycontrol, users, allnetworks, networks):
    if allnetworks == False and len(networks) == 0:
        raise Exception("Networks cannot be empty when allnetworks is false")

    with CursorFromPool() as cursor:
        sql = """
            insert into "group" ("name", "management", "data", "exporting", "processing", "qualitycontrol", "users", "allnetworks") 
            values (%(name)s, %(management)s, %(data)s, %(exporting)s, %(processing)s, %(qualitycontrol)s, %(users)s, %(allnetworks)s)
            returning "id"
        """
        o = {
            "name": name,
            "management": management,
            "data": data,
            "exporting": exporting,
            "processing": processing,
            "qualitycontrol": qualitycontrol,
            "qualitycontrol": qualitycontrol,
            "users": users,
            "allnetworks": allnetworks
        }
        cursor.execute(sql, o)
        groupid = cursor.fetchone()

        sql = "insert into groupnetwork (networkid, groupid) values (%(networkid)s, %(groupid)s)"
        for n in networks:
            cursor.execute(sql, {"networkid": n, "groupid": groupid["id"]})


def update_group(id, name, management, data, exporting, processing, qualitycontrol, users, allnetworks, networks):

    with CursorFromPool() as cursor:

        if is_locked_group(cursor, id):
            raise Exception("Cannot update locked group")

        if allnetworks == False and len(networks) == 0:
            raise Exception("Networks cannot be empty when allnetworks is false")

        sql = """
            update "group" 
            set
                "name"=%(name)s,
                "management"=%(management)s,
                "data"=%(data)s,
                "exporting"=%(exporting)s,
                "processing"=%(processing)s,
                "qualitycontrol"=%(qualitycontrol)s,
                "users"=%(users)s,
                "allnetworks"=%(allnetworks)s
            where "id"=%(id)s
        """

        o = {
            "name": name,
            "management": management,
            "data": data,
            "exporting": exporting,
            "processing": processing,
            "qualitycontrol": qualitycontrol,
            "qualitycontrol": qualitycontrol,
            "users": users,
            "allnetworks": allnetworks,
            "id": id
        }
        cursor.execute(sql, o)

        cursor.execute("delete from groupnetwork where groupid = %(groupid)s", {"groupid": id})

        if allnetworks != True:
            sql = "insert into groupnetwork (networkid, groupid) values (%(networkid)s, %(groupid)s)"
            for n in networks:
                cursor.execute(sql, {"networkid": n, "groupid": id})


def remove_group(id):
    with CursorFromPool() as cursor:
        if is_locked_group(cursor, id):
            raise Exception("Cannot delete locked group")

        sql = """delete from "group" where id = %(id)s"""
        cursor.execute(sql, {"id": id})


def is_locked_group(cursor, id):
    cursor.execute("""select 1 from "group" where id = %(id)s and locked = true""", {"id": id})
    return cursor.rowcount > 0
