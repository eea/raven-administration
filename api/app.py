from flask import Flask
from flask_cors import CORS
from flask_compress import Compress
from core.database import Database
from core.error import Error
from core.endpoints import Endpoints
from flask_jwt_extended import JWTManager
from config import Config

compress = Compress()
cors = CORS()
error = Error()
endpoints = Endpoints()
jwt = JWTManager()


app = Flask(__name__)
app.config.from_object(Config)

Database.init_app(app)
cors.init_app(app)
compress.init_app(app)
jwt.init_app(app)
error.init_app(app)
endpoints.init_app(app)
