class Endpoints:
    def init_app(self, app):
        from api.endpoints.auth.routes import auth_endpoint
        app.register_blueprint(auth_endpoint)

        # MANAGEMENT
        from api.endpoints.management.authorities.routes import authorities_endpoint
        app.register_blueprint(authorities_endpoint)

        from api.endpoints.management.networks.routes import networks_endpoint
        app.register_blueprint(networks_endpoint)

        from api.endpoints.management.stations.routes import stations_endpoint
        app.register_blueprint(stations_endpoint)

        # PROCESSING
        from api.endpoints.processing.calculate.routes import calculate_endpoint
        app.register_blueprint(calculate_endpoint)

        from api.endpoints.processing.convert.routes import convert_endpoint
        app.register_blueprint(convert_endpoint)

        from api.endpoints.processing.autovalidate.routes import autovalidate_endpoint
        app.register_blueprint(autovalidate_endpoint)

        # DATA
        from api.endpoints.data.historical.routes import historical_endpoint
        app.register_blueprint(historical_endpoint)

        from api.endpoints.data.latest.routes import latest_endpoint
        app.register_blueprint(latest_endpoint)

        # IMPORT
        from api.endpoints.imports.observations.routes import observations_endpoint
        app.register_blueprint(observations_endpoint)
