
import io


class Helper:
    @staticmethod
    def getScalingPoint(cursor, id):
        sql = """
            select * from scaling_points where id = %(id)s                       
        """
        cursor.execute(sql, {"id": id})
        scaling_point = cursor.fetchone()
        return scaling_point

    @staticmethod
    def _insertScalingPoint(cursor, zero_point, span_value, gas_concentration, timestamp, sampling_point_id, createdby):
        sql = """
            insert into scaling_points (zero_point, span_value, gas_concentration, timestamp, sampling_point_id, createdby)
            values (%(zero_point)s, %(span_value)s, %(gas_concentration)s, %(timestamp)s, %(sampling_point_id)s, %(createdby)s)
        """
        cursor.execute(sql, {"zero_point": zero_point, "span_value": span_value, "gas_concentration": gas_concentration, "timestamp": timestamp, "sampling_point_id": sampling_point_id, "createdby": createdby})
        return cursor.rowcount

    @staticmethod
    def _updateScalingPoint(cursor, id, zero_point, span_value, gas_concentration, timestamp, createdby):
        sql = """
            update scaling_points 
            set zero_point = %(zero_point)s,
            span_value = %(span_value)s,
            gas_concentration = %(gas_concentration)s,
            timestamp = %(timestamp)s,
            createdby = %(createdby)s
            where id = %(id)s
        """
        cursor.execute(sql, {"id": id, "zero_point": zero_point, "span_value": span_value, "gas_concentration": gas_concentration, "timestamp": timestamp,  "createdby": createdby})
        return cursor.rowcount

    @staticmethod
    def _deleteScalingPoint(cursor, id):
        sql = """
            delete from scaling_points where id = %(id)s                       
        """
        cursor.execute(sql, {"id": id})
        return cursor.rowcount

    @staticmethod
    def _insertScaledValues(cursor, values):
        sql = """            
            update observations
            set value = %(value)s,scaled_value = %(scaled_value)s,touched = now()
            where id = %(id)s
        """
        cursor.executemany(sql, values)
        return cursor.rowcount

    @staticmethod
    def _editScalingPoint(cursor, **kwargs):
        rows = Helper._updateScalingPoint(cursor, kwargs["id"], kwargs["zero_point"], kwargs["span_value"], kwargs["gas_concentration"], kwargs["timestamp"], kwargs["createdby"])
        if rows == 0:
            raise Exception("Could not update scaling point with id " + kwargs["id"])
        Helper._insertScaledValues(cursor, kwargs["observations"])
        return rows

    @staticmethod
    def editScalingPoint(cursor, id, zero_point, span_value, gas_concentration, timestamp, createdby, observations):
        return Helper._editScalingPoint(cursor, id=id, zero_point=zero_point, span_value=span_value, gas_concentration=gas_concentration, timestamp=timestamp, createdby=createdby, observations=observations)

    @staticmethod
    def _addScalingPoint(cursor, **kwargs):
        rows = Helper._insertScalingPoint(cursor, kwargs["zero_point"], kwargs["span_value"], kwargs["gas_concentration"], kwargs["timestamp"], kwargs["sampling_point_id"], kwargs["createdby"])
        if rows == 0:
            raise Exception("Could not insert scaling point")
        Helper._insertScaledValues(cursor, kwargs["observations"])
        return rows

    @staticmethod
    def addScalingPoint(cursor, zero_point, span_value, gas_concentration, timestamp, sampling_point_id, createdby, observations):
        return Helper._addScalingPoint(cursor, zero_point=zero_point, span_value=span_value, gas_concentration=gas_concentration, timestamp=timestamp, sampling_point_id=sampling_point_id, createdby=createdby, observations=observations)

    @staticmethod
    def _removeScalingPoint(curosr, **kwargs):
        rows = Helper._deleteScalingPoint(curosr, kwargs["id"])
        if rows == 0:
            raise Exception("Could not delete scaling point with id " + kwargs["id"])
        Helper._insertScaledValues(curosr, kwargs["observations"])
        return rows

    @staticmethod
    def removeScalingPoint(cursor, id, observations):
        return Helper._removeScalingPoint(cursor, id=id, observations=observations)
