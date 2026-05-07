class Groups:
    @staticmethod
    def get_members(cursor, sampling_point_id) -> list:
        """Returns IDs of all other group members for a given sampling point."""
        cursor.execute("""
            SELECT m.sampling_point_id AS id
            FROM sampling_point_group_members m
            WHERE m.group_id = (
                SELECT group_id FROM sampling_point_group_members WHERE sampling_point_id = %(sampling_point_id)s
            )
              AND m.sampling_point_id != %(sampling_point_id)s
        """, {"sampling_point_id": sampling_point_id})
        rows = cursor.fetchall()
        return [row["id"] for row in rows]
