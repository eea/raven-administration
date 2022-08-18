from flask import jsonify
from pydantic import ValidationError
from flask_pydantic import exceptions as py
from werkzeug.exceptions import HTTPException


class Error:
    def init_app(self, app):
        @app.errorhandler(HTTPException)
        def handle_exception(e):
            return jsonify(msg=str(e)), e.code

        @app.errorhandler(Exception)
        def handle_exception(e):
            return jsonify(msg=str(e)), 500

        @app.errorhandler(ValidationError)
        def handle_pydantic_validation_errors(e):
            return jsonify(msg=str(e.errors())), 400
