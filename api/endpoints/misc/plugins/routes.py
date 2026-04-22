import json
import os
import zipfile
import tempfile
import shutil
import logging

import requests
from flask import jsonify, Blueprint, request
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

        if os.path.isdir(extracted_api):
            dest_api = os.path.join(_API_PLUGINS_DIR, plugin_id)
            if os.path.exists(dest_api):
                shutil.rmtree(dest_api)
            shutil.copytree(extracted_api, dest_api)
            logger.info(f'Plugin {plugin_id}: backend files installed to {dest_api}')

        if os.path.isdir(extracted_client):
            dest_client = os.path.join(_CLIENT_PLUGINS_DIR, plugin_id)
            if os.path.exists(dest_client):
                shutil.rmtree(dest_client)
            shutil.copytree(extracted_client, dest_client)
            logger.info(f'Plugin {plugin_id}: frontend files installed to {dest_client}')

    # Register in DB (or upsert)
    with_cursor_insert = f"""
        INSERT INTO plugin_registry (id, name, version, description, restart_required)
        VALUES (%(id)s, %(name)s, %(version)s, %(description)s, TRUE)
        ON CONFLICT (id) DO UPDATE
            SET name = EXCLUDED.name,
                version = EXCLUDED.version,
                description = EXCLUDED.description,
                restart_required = TRUE,
                updated_at = NOW()
    """
    from core.database import CursorFromPool
    with CursorFromPool() as cursor:
        cursor.execute(with_cursor_insert, {
            "id": plugin_id, "name": name,
            "version": version, "description": description
        })

    return jsonify({"success": True, "restart_required": True})


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
