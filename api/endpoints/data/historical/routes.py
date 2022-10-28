from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from api.core.database import CursorFromPool
from api.endpoints.data.historical.models import HistoricalModel
from api.core.data.mean import Mean, MeanType
from api.core.jwt_ext_custom import jwt_required_with_observations_claim

historical_endpoint = Blueprint('historical', __name__)


@historical_endpoint.route('/api/data/historical', methods=['POST'])
@jwt_required_with_observations_claim()
def historical():
    with CursorFromPool() as cursor:
        m = HistoricalModel(**request.json)
        meanvalues = Mean.Aggregate(cursor, MeanType(m.meantype), tuple(m.sampling_point_ids), m.from_dt, m.to_dt, m.coverage, 3, 3, True)
        return jsonify(meanvalues)


## LOOKUPS ##

@historical_endpoint.route('/api/data/historical/timeseries', methods=['GET'])
@jwt_required_with_observations_claim()
def timeseries():
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT
              aa.value,
              CONCAT(aa.name,', ', aa.pollutant,', ', aa.timestep, ', ', aa.unit ) as label,
                  to_char(aa.fromtime, 'YYYY-MM-DD"T"HH24:MI:SS') as fromtime,
                  to_char(aa.totime, 'YYYY-MM-DD"T"HH24:MI:SS') as totime
              FROM
            (
              SELECT sp.id as sp, sp.id as value, s.name, po.notation pollutant,  sp.from_time as fromtime, sp.to_time as totime, t.label as timestep, u.notation as unit
                FROM
                    stations s,
                    sampling_points sp,
                    eea_pollutants po,
                    eea_times t,
                    eea_concentrations u
                WHERE 1=1
                    and s.id = sp.station_id
                    and sp.pollutant = po.uri
                    and sp.timestep = t.id
                    and sp.concentration = u.id
                    and sp.from_time is not null
                    and sp.to_time is not null
                GROUP by s.name, sp.id, sp.pollutant,sp.id, po.notation, sp.from_time,  sp.to_time, t.label, u.notation
            ) aa
            order by label
        """)
        timeseries = cursor.fetchall()
        return jsonify(timeseries)
