from flask_swagger_ui import get_swaggerui_blueprint
from config import Config
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class RavenSwagger:
    def init_app(self, app):
      config = Config()

      SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
      API_URL = config.SWAGGER_URL 

      # Call factory function to create our blueprint
      swaggerui_blueprint = get_swaggerui_blueprint(
          SWAGGER_URL,  # Swagger UI static files will be served in {SWAGGER_URL}/dist/
          API_URL,
          config={  # Swagger UI config overrides
              'app_name': "Reportnet3 Dataflow API"
          }
      )

      app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)