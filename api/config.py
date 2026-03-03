import os
from dotenv import load_dotenv
from datetime import datetime
from datetime import timedelta
from typing import Optional

basedir = os.path.abspath(os.path.dirname(__file__))

env_in_api = os.path.isfile(os.path.join(basedir, '.env'))
env_in_root = os.path.isfile(os.path.join(basedir, '../.env'))
path = os.path.join(basedir, '.env') if env_in_api else os.path.join(basedir, '../.env')


load_dotenv(path)

def get_variable(name: str, default_value: Optional[bool] = None) -> bool:
    true_ = ('true', '1', 't')
    false_ = ('false', '0', 'f')
    value: str | None = os.getenv(name, None)
    if value is None:
        if default_value is None:
            raise ValueError(f'Variable `{name}` not set!')
        else:
            value = str(default_value)
    if value.lower() not in true_ + false_:
        raise ValueError(f'Invalid value `{value}` for variable `{name}`')
    return value in true_

class Config(object):
    DB_URI = os.environ.get('DB_URI') or "postgresql://user:psw@localhost/db"
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES_SECONDS = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_SECONDS')) or 3600
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRES_SECONDS)
    SWAGGER_URL = os.environ.get('SWAGGER_URL') or 'http://localhost:5000/'
    
    # API Key for service-to-service authentication (Plans & Programs integration)
    # Set PLANS_PROGRAMS_API_KEY in .env file
    # Generate secure key: python -c "import secrets; print(secrets.token_urlsafe(32))"
    PLANS_PROGRAMS_API_KEY = os.environ.get('PLANS_PROGRAMS_API_KEY')