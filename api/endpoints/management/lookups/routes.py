from flask import jsonify, Blueprint, request
from core.jwt_ext_custom import jwt_required_with_management_claim
from core.database import CursorFromPool
from core.query import Q

management_endpoint = Blueprint('management', __name__)


## LOOKUPS ##
@management_endpoint.route('/api/management/lookups/areaclassifications', methods=['GET'])
@jwt_required_with_management_claim()
def areaclassifications():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_areaclassifications r order by r.label")
        areaclassifications = cursor.fetchall()
        return jsonify(areaclassifications)


@management_endpoint.route('/api/management/lookups/exceedancedescriptions', methods=['GET'])
@jwt_required_with_management_claim()
def exceedancedescriptions():
    with CursorFromPool() as cursor:
        cursor.execute("select r.name as label, r.id::varchar as value from eea_exceedancedescription r order by r.name")
        rows = cursor.fetchall()
        return jsonify(rows)


@management_endpoint.route('/api/management/lookups/exceedancetypes', methods=['GET'])
@jwt_required_with_management_claim()
def exceedancetypes():
    with CursorFromPool() as cursor:
        cursor.execute("select r.name as label, r.id::varchar as value from eea_exceedancetype r order by r.name")
        rows = cursor.fetchall()
        return jsonify(rows)


@management_endpoint.route('/api/management/lookups/adjustmentsourcetypes', methods=['GET'])
@jwt_required_with_management_claim()
def adjustmentsourcetypes():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_adjustmentsourcetype r order by r.label")
        rows = cursor.fetchall()
        return jsonify(rows)


@management_endpoint.route('/api/management/lookups/adjustmenttypes', methods=['GET'])
@jwt_required_with_management_claim()
def adjustmenttypes():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_adjustmenttypes r order by r.label")
        rows = cursor.fetchall()
        return jsonify(rows)


@management_endpoint.route('/api/management/lookups/reasons', methods=['GET'])
@jwt_required_with_management_claim()
def reasons():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_exceedancereason r order by r.label")
        rows = cursor.fetchall()
        return jsonify(rows)


@management_endpoint.route('/api/management/lookups/assessmentexceedances', methods=['GET'])
@jwt_required_with_management_claim()
def exceedances():
    with CursorFromPool() as cursor:
        cursor.execute("select r.id as label, r.id as value from eea_assessmentthresholdexceedances r order by r.id")
        equivdemonstrations = cursor.fetchall()
        return jsonify(equivdemonstrations)


@management_endpoint.route('/api/management/lookups/assessmenttypes', methods=['GET'])
@jwt_required_with_management_claim()
def assessmenttypes():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_assessmenttypes r order by r.label")
        assessmenttypes = cursor.fetchall()
        return jsonify(assessmenttypes)


@management_endpoint.route('/api/management/lookups/authorities', methods=['GET'])
@jwt_required_with_management_claim()
def authorities():
    with CursorFromPool() as cursor:
        cursor.execute("select r.name as label, r.id as value from responsible_authorities r order by r.name")
        authorities = cursor.fetchall()
        return jsonify(authorities)


@management_endpoint.route('/api/management/lookups/concentrations', methods=['GET'])
@jwt_required_with_management_claim()
def concentrations():
    with CursorFromPool() as cursor:
        cursor.execute("select r.notation as label, r.id as value from eea_concentrations r order by r.notation")
        concentrations = cursor.fetchall()
        return jsonify(concentrations)


@management_endpoint.route('/api/management/lookups/equivdemonstrations', methods=['GET'])
@jwt_required_with_management_claim()
def equivdemonstrations():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_equivalencedemonstrated r order by r.label")
        equivdemonstrations = cursor.fetchall()
        return jsonify(equivdemonstrations)


@management_endpoint.route('/api/management/lookups/levels', methods=['GET'])
@jwt_required_with_management_claim()
def levels():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_organisationallevels r order by r.label")
        authorities = cursor.fetchall()
        return jsonify(authorities)


@management_endpoint.route('/api/management/lookups/media', methods=['GET'])
@jwt_required_with_management_claim()
def media():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_mediavalues r order by r.label")
        authorities = cursor.fetchall()
        return jsonify(authorities)


@management_endpoint.route('/api/management/lookups/measurementequipment', methods=['GET'])
@jwt_required_with_management_claim()
def measurementequipment():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_measurementequipments r order by r.label")
        measurementequipment = cursor.fetchall()
        return jsonify(measurementequipment)


@management_endpoint.route('/api/management/lookups/measurementmethods', methods=['GET'])
@jwt_required_with_management_claim()
def measurement_methods():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_measurementmethods r order by r.label")
        measurement_methods = cursor.fetchall()
        return jsonify(measurement_methods)


@management_endpoint.route('/api/management/lookups/measurementregimes', methods=['GET'])
@jwt_required_with_management_claim()
def measurementregimes():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_measurementregimevalues r order by r.label")
        measurementregimes = cursor.fetchall()
        return jsonify(measurementregimes)


@management_endpoint.route('/api/management/lookups/measurementtypes', methods=['GET'])
@jwt_required_with_management_claim()
def measurementtypes():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_measurementtypes r order by r.label")
        measurementtypes = cursor.fetchall()
        return jsonify(measurementtypes)


@management_endpoint.route("/api/management/lookups/objecttypes", methods=['GET'])
@jwt_required_with_management_claim()
def objecttypes():
    with CursorFromPool() as cursor:
        cursor.execute("select id as value, id as label FROM eea_objecttypes order by id")
        rows = cursor.fetchall()
        return jsonify(rows)


@management_endpoint.route("/api/management/lookups/reportingmetrics", methods=['GET'])
@jwt_required_with_management_claim()
def reportingmetrics():
    with CursorFromPool() as cursor:
        cursor.execute("select id as value, id as label FROM eea_reportingmetrics order by id")
        rows = cursor.fetchall()
        return jsonify(rows)


@management_endpoint.route("/api/management/lookups/protectiontargets", methods=['GET'])
@jwt_required_with_management_claim()
def protectiontargets():
    with CursorFromPool() as cursor:
        cursor.execute("select id as value, id as label FROM eea_protectiontargets order by id")
        rows = cursor.fetchall()
        return jsonify(rows)


@management_endpoint.route('/api/management/lookups/processtypevalues', methods=['GET'])
@jwt_required_with_management_claim()
def processtypevalues():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_processtypevalues r order by r.label")
        processtypevalues = cursor.fetchall()
        return jsonify(processtypevalues)


@management_endpoint.route('/api/management/lookups/pollutants', methods=['GET'])
@jwt_required_with_management_claim()
def pollutants():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.uri as value from eea_pollutants r order by r.label")
        pollutants = cursor.fetchall()
        return jsonify(pollutants)


@management_endpoint.route('/api/management/lookups/responsibleauthorities', methods=['GET'])
@jwt_required_with_management_claim()
def responsibleauthorities():
    with CursorFromPool() as cursor:
        cursor.execute("select r.name as label, r.id as value from responsible_authorities r order by r.name")
        responsibleauthorities = cursor.fetchall()
        return jsonify(responsibleauthorities)


@management_endpoint.route('/api/management/lookups/resultnaturevalues', methods=['GET'])
@jwt_required_with_management_claim()
def resultnaturevalues():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_resultnaturevalues r order by r.label")
        resultnaturevalues = cursor.fetchall()
        return jsonify(resultnaturevalues)


@management_endpoint.route('/api/management/lookups/stationclassifications', methods=['GET'])
@jwt_required_with_management_claim()
def station_classifications():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_stationclassifications r order by r.label")
        station_classifications = cursor.fetchall()
        return jsonify(station_classifications)


@management_endpoint.route('/api/management/lookups/zones_types', methods=['GET'])
@jwt_required_with_management_claim()
def zones_types():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_zonetypes r order by r.label")
        rows = cursor.fetchall()
        return jsonify(rows)


@management_endpoint.route('/api/management/lookups/timezones', methods=['GET'])
@jwt_required_with_management_claim()
def timezones():
    timezones = Q.timezones()
    return jsonify(timezones)


@management_endpoint.route('/api/management/lookups/timesteps', methods=['GET'])
@jwt_required_with_management_claim()
def timesteps():
    type = request.args.get("type", default="aq", type=str)
    with CursorFromPool() as cursor:
        cursor.execute("""
        select r.label as label, r.id as value
        from eea_times r
        where r.id ~ %(type)s
        order by r.label
        """, {"type": "vocabulary/" + type})
        timesteps = cursor.fetchall()
        return jsonify(timesteps)


@management_endpoint.route('/api/management/lookups/attainments', methods=['GET'])
@jwt_required_with_management_claim()
def attainments():
    with CursorFromPool() as cursor:
        cursor.execute("select r.name as label, r.id as value from attainments r order by r.name")
        processes = cursor.fetchall()
        return jsonify(processes)


@management_endpoint.route('/api/management/lookups/assessmentregimes', methods=['GET'])
@jwt_required_with_management_claim()
def assessmentregimes():
    with CursorFromPool() as cursor:
        cursor.execute("select r.name as label, r.id as value from assessmentregimes r order by r.name")
        processes = cursor.fetchall()
        return jsonify(processes)


@management_endpoint.route('/api/management/lookups/processes', methods=['GET'])
@jwt_required_with_management_claim()
def processes():
    with CursorFromPool() as cursor:
        cursor.execute("select r.id as label, r.id as value from processes r order by r.id")
        processes = cursor.fetchall()
        return jsonify(processes)


@management_endpoint.route('/api/management/lookups/samples', methods=['GET'])
@jwt_required_with_management_claim()
def samples():
    with CursorFromPool() as cursor:
        cursor.execute("select r.id as label, r.id as value from samples r order by r.id")
        samples = cursor.fetchall()
        return jsonify(samples)


@management_endpoint.route('/api/management/lookups/zones', methods=['GET'])
@jwt_required_with_management_claim()
def zones():
    with CursorFromPool() as cursor:
        cursor.execute("select r.name as label, r.id as value from zones r order by r.name")
        zones = cursor.fetchall()
        return jsonify(zones)


@management_endpoint.route('/api/management/lookups/networks', methods=['GET'])
@jwt_required_with_management_claim()
def networks():
    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        cursor.execute(f"""
          {with_network_sql}
          select n.name as label, n.id as value from networks n, network_access na where n.id = na.id order by n.name
        """, n_param)
        networks = cursor.fetchall()
        return jsonify(networks)


@management_endpoint.route('/api/management/lookups/samplingpoints', methods=['GET'])
@jwt_required_with_management_claim()
def samplingpoints():
    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.with_sampling_points_by_networks_access()
        cursor.execute(f"""
          {with_network_sql}
          select r.id as label, r.id as value from sampling_points r, sampling_point_access spa where r.id = spa.id order by r.id
        """, n_param)
        samplingpoints = cursor.fetchall()
        return jsonify(samplingpoints)


@management_endpoint.route('/api/management/lookups/samplingpoints_extended', methods=['GET'])
@jwt_required_with_management_claim()
def samplingpoints_extended():
    samplingpoints = Q.timeseries_by_access()
    return jsonify(samplingpoints)


@management_endpoint.route('/api/management/lookups/stations', methods=['GET'])
@jwt_required_with_management_claim()
def stations():
    with_network_sql, n_param = Q.with_networks_by_access_as_sql()
    with CursorFromPool() as cursor:
        cursor.execute(f"""
          {with_network_sql}
          select r.name as label, r.id as value from stations r, network_access na where r.network_id = na.id order by r.name
        """, n_param)
        stations = cursor.fetchall()
        return jsonify(stations)
