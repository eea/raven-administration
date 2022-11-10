class Endpoints:
    def init_app(self, app):
        from api.endpoints.auth.routes import auth_endpoint
        app.register_blueprint(auth_endpoint)

        # MANAGEMENT
        from api.endpoints.management.lookups.routes import management_endpoint
        app.register_blueprint(management_endpoint)

        from api.endpoints.management.assessmentregimes.routes import assessmentregimes_endpoint
        app.register_blueprint(assessmentregimes_endpoint)

        from api.endpoints.management.authorities.routes import authorities_endpoint
        app.register_blueprint(authorities_endpoint)

        from api.endpoints.management.networks.routes import networks_endpoint
        app.register_blueprint(networks_endpoint)

        from api.endpoints.management.stations.routes import stations_endpoint
        app.register_blueprint(stations_endpoint)

        from api.endpoints.management.samplingpoints.routes import samplingpoints_endpoint
        app.register_blueprint(samplingpoints_endpoint)

        from api.endpoints.management.processes.routes import processes_endpoint
        app.register_blueprint(processes_endpoint)

        from api.endpoints.management.samples.routes import samples_endpoint
        app.register_blueprint(samples_endpoint)

        from api.endpoints.management.observingcapabilities.routes import observingcapabilities_endpoint
        app.register_blueprint(observingcapabilities_endpoint)

        from api.endpoints.management.zones.routes import zones_endpoint
        app.register_blueprint(zones_endpoint)

        # PROCESSING
        from api.endpoints.processing.scale.routes import scale_endpoint
        app.register_blueprint(scale_endpoint)

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

        from api.endpoints.data.dataflow.routes import dataflow_endpoint
        app.register_blueprint(dataflow_endpoint)

        # QUALITY CONTROL
        from api.endpoints.qualitycontrol.validate.routes import validate_endpoint
        app.register_blueprint(validate_endpoint)

        from api.endpoints.qualitycontrol.verify.routes import verify_endpoint
        app.register_blueprint(verify_endpoint)

        # ACCESS
        from api.endpoints.access.routes import access_endpoint
        app.register_blueprint(access_endpoint)

        # IMPORT
        from api.endpoints.imports.observations.routes import observations_endpoint
        app.register_blueprint(observations_endpoint)
