from flask import jsonify
from pydantic import ValidationError
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
            # Extract the first error message from Pydantic validation errors
            errors = e.errors()
            if errors and len(errors) > 0:
                first_error = errors[0]
                field = " -> ".join(str(loc) for loc in first_error.get('loc', []))
                message = first_error.get('msg', 'Validation error')
                error_msg = f"{field}: {message}" if field else message
            else:
                error_msg = "Validation error"
            
            return jsonify(msg=error_msg), 400
