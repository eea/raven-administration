import os
from dotenv import load_dotenv
from datetime import datetime
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    DB_URI = os.environ.get('DB_URI') or "postgresql://user:psw@localhost/db"
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES_SECONDS = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_SECONDS')) or 3600
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRES_SECONDS)
