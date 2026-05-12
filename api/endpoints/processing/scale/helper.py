
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
        """
        Upsert scaled observations using (sampling_point_id, from_time, to_time) as the match key.
        Updates existing rows (NOX, NO2 etc) and inserts new rows (calculated results like NO
        that don't yet exist in observations).
        """
        if not values or len(values) == 0:
            return 0

        cursor.execute("""
            CREATE TEMP TABLE IF NOT EXISTS temp_scaled_values (
                sampling_point_id varchar(100),
                from_time timestamp,
                to_time timestamp,
                value DOUBLE PRECISION,
                scaled_value DOUBLE PRECISION,
                import_value DOUBLE PRECISION,
                observationverification_id integer,
                observationvalidity_id integer
            ) ON COMMIT DROP
        """)
        cursor.execute("TRUNCATE temp_scaled_values")

        buffer = io.StringIO()
        for row in values:
            sp_id = row.get("sampling_point_id")
            from_t = row.get("from_time")
            to_t = row.get("to_time")
            if not sp_id or from_t is None or to_t is None:
                continue

            def _v(x):
                return "\\N" if x is None or (isinstance(x, float) and __import__('math').isnan(x)) else x

            val = _v(row.get("value"))
            scaled = _v(row.get("scaled_value"))
            imp = _v(row.get("import_value"))
            ver = _v(row.get("observationverification_id"))
            validity = _v(row.get("observationvalidity_id"))
            ft_str = from_t.isoformat() if hasattr(from_t, "isoformat") else str(from_t)
            tt_str = to_t.isoformat() if hasattr(to_t, "isoformat") else str(to_t)
            buffer.write(f"{sp_id}\t{ft_str}\t{tt_str}\t{val}\t{scaled}\t{imp}\t{ver}\t{validity}\n")
        buffer.seek(0)

        cursor.copy_from(buffer, "temp_scaled_values", columns=("sampling_point_id", "from_time", "to_time", "value", "scaled_value", "import_value", "observationverification_id", "observationvalidity_id"))

        # Update existing rows
        cursor.execute("""
            UPDATE observations o
            SET value = t.value,
                scaled_value = t.scaled_value,
                touched = now()
            FROM temp_scaled_values t
            WHERE o.sampling_point_id = t.sampling_point_id
            AND o.from_time = t.from_time
            AND o.to_time = t.to_time
        """)

        # Insert rows that don't exist yet (e.g. calculated results like NO)
        cursor.execute("""
            INSERT INTO observations (sampling_point_id, from_time, to_time, value, scaled_value, import_value, observationverification_id, observationvalidity_id, touched)
            SELECT t.sampling_point_id, t.from_time, t.to_time, t.value, t.scaled_value, t.import_value, t.observationverification_id, t.observationvalidity_id, now()
            FROM temp_scaled_values t
            WHERE NOT EXISTS (
                SELECT 1 FROM observations o
                WHERE o.sampling_point_id = t.sampling_point_id
                AND o.from_time = t.from_time
                AND o.to_time = t.to_time
            )
        """)

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
    def _removeScalingPoint(cursor, **kwargs):
        rows = Helper._deleteScalingPoint(cursor, kwargs["id"])
        if rows == 0:
            raise Exception("Could not delete scaling point with id " + kwargs["id"])
        Helper._insertScaledValues(cursor, kwargs["observations"])
        return rows

    @staticmethod
    def removeScalingPoint(cursor, id, observations):
        return Helper._removeScalingPoint(cursor, id=id, observations=observations)
