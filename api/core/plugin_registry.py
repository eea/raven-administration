from core.database import CursorFromPool


class PluginRegistry:

    @staticmethod
    def self_register(plugin_id: str, name: str, version: str, description: str) -> None:
        """Called by each plugin's register(app) to upsert its metadata. Preserves existing enabled/config."""
        with CursorFromPool() as cursor:
            cursor.execute("""
                INSERT INTO plugin_registry (id, name, version, description)
                VALUES (%(id)s, %(name)s, %(version)s, %(description)s)
                ON CONFLICT (id) DO UPDATE
                    SET name = EXCLUDED.name,
                        version = EXCLUDED.version,
                        description = EXCLUDED.description,
                        updated_at = NOW()
            """, {"id": plugin_id, "name": name, "version": version, "description": description})

    @staticmethod
    def list_all() -> list:
        with CursorFromPool() as cursor:
            cursor.execute("SELECT * FROM plugin_registry ORDER BY name")
            return cursor.fetchall()

    @staticmethod
    def get(plugin_id: str) -> dict | None:
        with CursorFromPool() as cursor:
            cursor.execute("SELECT * FROM plugin_registry WHERE id = %s", (plugin_id,))
            return cursor.fetchone()

    @staticmethod
    def set_enabled(plugin_id: str, enabled: bool) -> None:
        with CursorFromPool() as cursor:
            cursor.execute(
                "UPDATE plugin_registry SET enabled = %s, updated_at = NOW() WHERE id = %s",
                (enabled, plugin_id)
            )

    @staticmethod
    def get_config(plugin_id: str) -> dict:
        with CursorFromPool() as cursor:
            cursor.execute("SELECT config FROM plugin_registry WHERE id = %s", (plugin_id,))
            row = cursor.fetchone()
            return row["config"] if row else {}

    @staticmethod
    def set_config(plugin_id: str, config: dict) -> None:
        import json
        with CursorFromPool() as cursor:
            cursor.execute(
                "UPDATE plugin_registry SET config = %s::jsonb, updated_at = NOW() WHERE id = %s",
                (json.dumps(config), plugin_id)
            )

    @staticmethod
    def set_config_json(plugin_id: str, config_json: str) -> None:
        """Save config as a raw JSON string (safe for arbitrary JSON content)."""
        with CursorFromPool() as cursor:
            cursor.execute(
                "UPDATE plugin_registry SET config = %s::jsonb, updated_at = NOW() WHERE id = %s",
                (config_json, plugin_id)
            )

    @staticmethod
    def mark_restart_required(plugin_id: str) -> None:
        with CursorFromPool() as cursor:
            cursor.execute(
                "UPDATE plugin_registry SET restart_required = TRUE, updated_at = NOW() WHERE id = %s",
                (plugin_id,)
            )

    @staticmethod
    def clear_restart_required(plugin_id: str) -> None:
        with CursorFromPool() as cursor:
            cursor.execute(
                "UPDATE plugin_registry SET restart_required = FALSE, updated_at = NOW() WHERE id = %s",
                (plugin_id,)
            )

    @staticmethod
    def any_restart_required() -> bool:
        with CursorFromPool() as cursor:
            cursor.execute("SELECT EXISTS(SELECT 1 FROM plugin_registry WHERE restart_required = TRUE)")
            row = cursor.fetchone()
            return row["exists"] if row else False
