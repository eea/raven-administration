import json
import os
import signal
import zipfile
import tempfile
import shutil
import logging

import requests
from flask import jsonify, Blueprint, request, current_app
from werkzeug.exceptions import BadRequest, NotFound
from core.jwt_ext_custom import jwt_required_with_management_claim, jwt_required_with_allnetworks_claim
from core.plugin_registry import PluginRegistry

logger = logging.getLogger(__name__)

plugins_manager_endpoint = Blueprint('plugins_manager', __name__)

# Base path for plugin installation (relative to this file: api/core/../plugins → api/plugins)
_API_PLUGINS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../plugins'))
_CLIENT_PLUGINS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../../client/src/plugins'))


@plugins_manager_endpoint.route('/api/misc/plugins', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def list_plugins():
    plugins = PluginRegistry.list_all()
    return jsonify(plugins)


@plugins_manager_endpoint.route('/api/misc/plugins/enabled', methods=['GET'])
def list_enabled_plugins():
    """Public endpoint: returns enabled plugin IDs with has_client flag.
    Used by the frontend to inject runtime plugin scripts without a build step."""
    from core.database import CursorFromPool
    with CursorFromPool() as cursor:
        cursor.execute("SELECT id FROM plugin_registry WHERE enabled = TRUE ORDER BY name")
        rows = cursor.fetchall()
    result = []
    for row in rows:
        pid = row['id']
        has_client = os.path.isfile(os.path.join(_API_PLUGINS_DIR, pid, 'client.js'))
        result.append({'id': pid, 'has_client': has_client})
    return jsonify(result)


@plugins_manager_endpoint.route('/api/plugins/<plugin_id>/client.js', methods=['GET'])
def serve_plugin_client(plugin_id: str):
    """Public endpoint: serves a plugin's client-side JS for runtime loading.
    Allows plugins to work in Kubernetes without rebuilding the Docker image."""
    client_js = os.path.join(_API_PLUGINS_DIR, plugin_id, 'client.js')
    if not os.path.isfile(client_js):
        return ('', 404)
    with open(client_js, 'r', encoding='utf-8') as f:
        content = f.read()
    return current_app.response_class(content, mimetype='application/javascript')


@plugins_manager_endpoint.route('/api/misc/plugins/catalog', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def plugin_catalog():
    registry_url = os.environ.get('PLUGIN_REGISTRY_URL', 'https://raven-plugins.nilu.no/api/catalog')
    try:
        resp = requests.get(registry_url, timeout=10)
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.RequestException as e:
        logger.error(f'Failed to fetch plugin catalog: {e}')
        return jsonify([])


@plugins_manager_endpoint.route('/api/misc/plugins/install', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def install_plugin():
    data = request.json or {}
    plugin_id = data.get('id')
    download_url = data.get('download_url')
    name = data.get('name', plugin_id)
    version = data.get('version', 'unknown')
    description = data.get('description', '')

    if not plugin_id or not download_url:
        raise BadRequest('id and download_url are required')

    try:
        resp = requests.get(download_url, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise BadRequest(f'Failed to download plugin: {e}')

    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, 'plugin.zip')
        with open(zip_path, 'wb') as f:
            f.write(resp.content)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(tmp_dir)
        except zipfile.BadZipFile:
            raise BadRequest('Downloaded file is not a valid zip archive')

        # Expected structure inside zip: api/ and client/
        extracted_api = os.path.join(tmp_dir, 'api')
        extracted_client = os.path.join(tmp_dir, 'client')

        # Detect whether the plugin has Python backend code — requires a gunicorn restart.
        has_backend = os.path.isdir(extracted_api) and os.path.isfile(
            os.path.join(extracted_api, '__init__.py')
        )

        if os.path.isdir(extracted_api):
            dest_api = os.path.join(_API_PLUGINS_DIR, plugin_id)
            if os.path.exists(dest_api):
                shutil.rmtree(dest_api)
            shutil.copytree(extracted_api, dest_api)
            logger.info(f'Plugin {plugin_id}: backend files installed to {dest_api}')

        if os.path.isdir(extracted_client):
            # Store client.js in the API plugins dir so it can be served at runtime
            # (works in both Docker Compose and Kubernetes without a rebuild)
            client_index = os.path.join(extracted_client, 'index.js')
            if os.path.isfile(client_index):
                dest_api_dir = os.path.join(_API_PLUGINS_DIR, plugin_id)
                os.makedirs(dest_api_dir, exist_ok=True)
                shutil.copy2(client_index, os.path.join(dest_api_dir, 'client.js'))
                logger.info(f'Plugin {plugin_id}: client.js stored for runtime serving')

            # Also copy to client/src/plugins/ for dev-mode Vite build (optional, may not exist in K8s)
            try:
                dest_client = os.path.join(_CLIENT_PLUGINS_DIR, plugin_id)
                if os.path.exists(dest_client):
                    shutil.rmtree(dest_client)
                shutil.copytree(extracted_client, dest_client)
                logger.info(f'Plugin {plugin_id}: frontend files installed to {dest_client}')
            except OSError:
                logger.info(f'Plugin {plugin_id}: client/src/plugins not available (runtime-only mode)')

    # restart_required = True only for plugins with Python backend code (__init__.py).
    # Frontend-only plugins are served dynamically and activate on a simple page reload.
    upsert_sql = """
        INSERT INTO plugin_registry (id, name, version, description, restart_required)
        VALUES (%(id)s, %(name)s, %(version)s, %(description)s, %(restart_required)s)
        ON CONFLICT (id) DO UPDATE
            SET name = EXCLUDED.name,
                version = EXCLUDED.version,
                description = EXCLUDED.description,
                restart_required = EXCLUDED.restart_required,
                updated_at = NOW()
    """
    from core.database import CursorFromPool
    with CursorFromPool() as cursor:
        cursor.execute(upsert_sql, {
            "id": plugin_id, "name": name,
            "version": version, "description": description,
            "restart_required": has_backend,
        })

    return jsonify({"success": True, "restart_required": has_backend})


@plugins_manager_endpoint.route('/api/misc/plugins/<plugin_id>/enable', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def enable_plugin(plugin_id: str):
    plugin = PluginRegistry.get(plugin_id)
    if not plugin:
        raise NotFound(f'Plugin {plugin_id} not found')
    PluginRegistry.set_enabled(plugin_id, True)
    return jsonify({"success": True})


@plugins_manager_endpoint.route('/api/misc/plugins/<plugin_id>/disable', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def disable_plugin(plugin_id: str):
    plugin = PluginRegistry.get(plugin_id)
    if not plugin:
        raise NotFound(f'Plugin {plugin_id} not found')
    PluginRegistry.set_enabled(plugin_id, False)
    return jsonify({"success": True})


@plugins_manager_endpoint.route('/api/misc/plugins/<plugin_id>/config', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def get_plugin_config(plugin_id: str):
    plugin = PluginRegistry.get(plugin_id)
    if not plugin:
        raise NotFound(f'Plugin {plugin_id} not found')
    return jsonify(plugin["config"] or {})


@plugins_manager_endpoint.route('/api/misc/plugins/<plugin_id>/config', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def save_plugin_config(plugin_id: str):
    plugin = PluginRegistry.get(plugin_id)
    if not plugin:
        raise NotFound(f'Plugin {plugin_id} not found')
    config = request.json or {}
    PluginRegistry.set_config_json(plugin_id, json.dumps(config))
    return jsonify({"success": True})


@plugins_manager_endpoint.route('/api/misc/plugins/restart', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def restart_server():
    """Restart the gunicorn server to load newly installed backend plugin code.
    Works in Docker (restart: always brings it back). Returns 400 in K8s/unknown environments."""
    # Heuristic: a shared client-dist volume mounted at /app/client/dist indicates Docker Compose.
    # In K8s the API pod has no client source — the restart must be done via kubectl/ArgoCD.
    is_docker = os.path.isdir('/app/client/dist')
    if not is_docker:
        raise BadRequest(
            'Server restart via API is only supported in Docker deployments. '
            'In Kubernetes, restart the raven-api pod via ArgoCD or: '
            'kubectl rollout restart deployment/raven-api'
        )

    from core.database import CursorFromPool
    with CursorFromPool() as cursor:
        cursor.execute("UPDATE plugin_registry SET restart_required = FALSE, updated_at = NOW()")

    logger.info('Restarting gunicorn via SIGTERM on parent process')
    # Send SIGTERM to the gunicorn master. Docker restart:always will bring the container back.
    os.kill(os.getppid(), signal.SIGTERM)
    return jsonify({"success": True})
