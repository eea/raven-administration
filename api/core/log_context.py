from core.jwt_ext_custom import get_name


def set_log_context(cursor, change_source: str) -> None:
    """
    Set PostgreSQL session-local GUCs so the observation_log trigger
    can capture who made the change and why.

    Must be called within the same CursorFromPool transaction BEFORE any
    UPDATE to the observations table:

        with CursorFromPool() as cursor:
            set_log_context(cursor, 'qc_verify')
            cursor.execute("UPDATE observations SET ...")

    Valid change_source values: 'qc_verify', 'qc_validate', 'scaling', 'adacs_import'
    """
    try:
        username = get_name()
    except Exception:
        username = None

    cursor.execute(
        "SELECT set_config('app.username', %s, true), set_config('app.change_source', %s, true)",
        (username or "", change_source)
    )
