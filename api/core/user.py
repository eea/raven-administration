from datetime import datetime
from api.core.database import CursorFromPool
from pydantic import BaseModel
from werkzeug.security import check_password_hash, generate_password_hash
from typing import Optional


class User(BaseModel):
    id: str
    name: str
    username: str


# USER
def get_user(username, password):
    with CursorFromPool() as cursor:
        sql = """
             select id, name, username, password
             from users
             where username = %(username)s
        """
        cursor.execute(sql, {"username": username})
        user = cursor.fetchone()

        if user == None or check_password_hash(user["password"], password) == False:
            return None

        return User(**user)


def remove_user(id):
    with CursorFromPool() as cursor:
        sql = "delete from users where id = %(id)s"
        cursor.execute(sql, {"id": id})


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
        sql = """update users set username=%(username)s, password=%(password)s, name=%(name)s, createdby=%(createdby)s, created=%(created)s where "id"=%(id)s"""

        if password == "" or password == None:
            sql = """update users set username=%(username)s, name=%(name)s, createdby=%(createdby)s, created=%(created)s where "id"=%(id)s"""

        o = {
            "username": username,
            "createdby": createdby,
            "created": datetime.now(tz=None),
            "name": name,
            "id": id
        }
        if not (password == "" or password == None):
            o["password"] = generate_password_hash(password)
        cursor.execute(sql, o)

        cursor.execute("delete from usergroup where userid = %(userid)s", {"userid": id})

        sql = "insert into usergroup (groupid, userid) values (%(groupid)s, %(userid)s)"
        for g in groups:
            cursor.execute(sql, {"groupid": g, "userid": id})


# GROUP
def add_group(name, network, observations, exporting, processing, qualitycontrol, users, allnetworks, networks):
    if allnetworks == False and len(networks) == 0:
        raise Exception("Networks cannot be empty when allnetworks is false")

    with CursorFromPool() as cursor:
        sql = """
            insert into "group" ("name", "network", "observations", "exporting", "processing", "qualitycontrol", "users", "allnetworks") 
            values (%(name)s, %(network)s, %(observations)s, %(exporting)s, %(processing)s, %(qualitycontrol)s, %(users)s, %(allnetworks)s)
            returning "id"
        """
        o = {
            "name": name,
            "network": network,
            "observations": observations,
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


def update_group(id, name, network, observations, exporting, processing, qualitycontrol, users, allnetworks, networks):
    if allnetworks == False and len(networks) == 0:
        raise Exception("Networks cannot be empty when allnetworks is false")

    with CursorFromPool() as cursor:
        sql = """
            update "group" 
            set
                "name"=%(name)s,
                "network"=%(network)s,
                "observations"=%(observations)s,
                "exporting"=%(exporting)s,
                "processing"=%(processing)s,
                "qualitycontrol"=%(qualitycontrol)s,
                "users"=%(users)s,
                "allnetworks"=%(allnetworks)s
            where "id"=%(id)s
        """

        o = {
            "name": name,
            "network": network,
            "observations": observations,
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
        sql = """delete from "group" where id = %(id)s"""
        cursor.execute(sql, {"id": id})
