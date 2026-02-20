class Endpoints:
    def init_app(self, app):
        # HEALTH CHECK (no auth required)
        from endpoints.health.routes import health_endpoint
        app.register_blueprint(health_endpoint)
        
        from endpoints.auth.routes import auth_endpoint
        app.register_blueprint(auth_endpoint)

        # MANAGEMENT
        from endpoints.management.lookups.routes import management_endpoint
        app.register_blueprint(management_endpoint)

        from endpoints.management.authorities.routes import authorities_endpoint
        app.register_blueprint(authorities_endpoint)

        from endpoints.management.zones.routes import zones_endpoint
        app.register_blueprint(zones_endpoint)

        from endpoints.management.networks.routes import networks_endpoint
        app.register_blueprint(networks_endpoint)

        from endpoints.management.stations.routes import stations_endpoint
        app.register_blueprint(stations_endpoint)

        from endpoints.management.samplingpoints.routes import samplingpoints_endpoint
        app.register_blueprint(samplingpoints_endpoint)

        from endpoints.management.processes.routes import processes_endpoint
        app.register_blueprint(processes_endpoint)

        from endpoints.management.samples.routes import samples_endpoint
        app.register_blueprint(samples_endpoint)

        from endpoints.management.observingcapabilities.routes import observingcapabilities_endpoint
        app.register_blueprint(observingcapabilities_endpoint)

        from endpoints.management.assessmentregimes.routes import assessmentregimes_endpoint
        app.register_blueprint(assessmentregimes_endpoint)

        from endpoints.management.attainments.routes import attainments_endpoint
        app.register_blueprint(attainments_endpoint)

        from endpoints.management.exceedances.routes import exceedances_endpoint
        app.register_blueprint(exceedances_endpoint)

        # PROCESSING
        from endpoints.processing.scale.routes import scale_endpoint
        app.register_blueprint(scale_endpoint)

        from endpoints.processing.calculate.routes import calculate_endpoint
        app.register_blueprint(calculate_endpoint)

        from endpoints.processing.convert.routes import convert_endpoint
        app.register_blueprint(convert_endpoint)

        from endpoints.processing.autovalidate.routes import autovalidate_endpoint
        app.register_blueprint(autovalidate_endpoint)

        # DATA
        from endpoints.data.historical.routes import historical_endpoint
        app.register_blueprint(historical_endpoint)

        from endpoints.data.latest.routes import latest_endpoint
        app.register_blueprint(latest_endpoint)

        from endpoints.data.dataflow.routes import dataflow_endpoint
        app.register_blueprint(dataflow_endpoint)

        from endpoints.data.statistics.routes import statistics_endpoint
        app.register_blueprint(statistics_endpoint)

        from endpoints.data.exceedances.routes import exceedances_endpoint
        app.register_blueprint(exceedances_endpoint)

        from endpoints.data.map.routes import map_endpoint
        app.register_blueprint(map_endpoint)

        from endpoints.data.rnotebook.routes import r_notebook_endpoint
        app.register_blueprint(r_notebook_endpoint)

        # QUALITY CONTROL
        from endpoints.qualitycontrol.validate.routes import validate_endpoint
        app.register_blueprint(validate_endpoint)

        from endpoints.qualitycontrol.verify.routes import verify_endpoint
        app.register_blueprint(verify_endpoint)

        # MISC
        from endpoints.misc.settings.routes import settings_endpoint
        app.register_blueprint(settings_endpoint)

        from endpoints.misc.preaggregation.routes import preagg_endpoint
        app.register_blueprint(preagg_endpoint)

        from endpoints.misc.aqi.routes import aqi_endpoint
        app.register_blueprint(aqi_endpoint)

        from endpoints.misc.notifications.routes import notifications_endpoint
        app.register_blueprint(notifications_endpoint)

        # ACCESS
        from endpoints.access.routes import access_endpoint
        app.register_blueprint(access_endpoint)

        # IMPORT
        from endpoints.imports.observations.routes import observations_endpoint
        app.register_blueprint(observations_endpoint)

        from endpoints.imports.management.routes import import_management_endpoint
        app.register_blueprint(import_management_endpoint)

        # EXPORT
        from endpoints.exports.management.routes import export_management_endpoint
        app.register_blueprint(export_management_endpoint)

        from endpoints.exports.observations.routes import export_observations_endpoint
        app.register_blueprint(export_observations_endpoint)

        from endpoints.exports.plans_programs.routes import plans_programs_endpoint
        app.register_blueprint(plans_programs_endpoint)

        # VERSION
        from endpoints.version.routes import version_endpoint
        app.register_blueprint(version_endpoint)
