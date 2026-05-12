class Groups:
    @staticmethod
    def get_members(cursor, sampling_point_id) -> list:
        """Returns IDs of all other group members for a given sampling point."""
        cursor.execute("""
            SELECT sampling_point_id AS id
            FROM sampling_point_groups
            WHERE group_id = (
                SELECT group_id FROM sampling_point_groups WHERE sampling_point_id = %(sampling_point_id)s
            )
              AND sampling_point_id != %(sampling_point_id)s
        """, {"sampling_point_id": sampling_point_id})
        return [row["id"] for row in cursor.fetchall()]

    @staticmethod
    def is_calculated(cursor, sp_id) -> bool:
        """Returns True if the sampling point is the result of a calculated series."""
        cursor.execute(
            "SELECT 1 FROM calculated_series WHERE result = %(sp_id)s LIMIT 1",
            {"sp_id": sp_id}
        )
        return cursor.fetchone() is not None

    @staticmethod
    def get_members_with_info(cursor, sp_id) -> list:
        """Returns [{id, pollutant}] for non-calculated group members of the given SP."""
        cursor.execute("""
            SELECT g.sampling_point_id AS id,
                   COALESCE(NULLIF(p.notation, ''), p.label) AS pollutant
            FROM sampling_point_groups g
            JOIN sampling_points sp ON sp.id = g.sampling_point_id
            JOIN eea_pollutants p ON p.id = sp.pollutant_id
            WHERE g.group_id = (
                SELECT group_id FROM sampling_point_groups WHERE sampling_point_id = %(sp_id)s
            )
              AND g.sampling_point_id != %(sp_id)s
              AND NOT EXISTS (SELECT 1 FROM calculated_series cs WHERE cs.result = g.sampling_point_id)
        """, {"sp_id": sp_id})
        return cursor.fetchall()
