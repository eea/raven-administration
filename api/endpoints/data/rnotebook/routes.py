# api/r_runner/routes.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
import requests
import subprocess
import tempfile
import os
from urllib.parse import urlparse, unquote

R_API_TIMEOUT = 300  # 5 minutes timeout for R operations

# Always use the rfiles folder relative to the project root
RFILES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../rfiles'))
os.makedirs(RFILES_DIR, exist_ok=True)

# Base URL of the R API
R_API_URL = os.environ.get('R_API_URL', 'http://127.0.0.1:8888')

r_notebook_endpoint = Blueprint('r_notebook', __name__)

def ensure_ravendb_conn() -> bool:
    """Ensure an R connection object named `ravendb_conn` exists in the R session.

    - Calls the R runner `/ls` endpoint and checks for `ravendb_conn`.
    - If missing, parses DB_URI from config or environment and posts a `/run` command
      to create `ravendb_conn` with dbConnect(RPostgres::Postgres(), ...).

    Returns True if the object exists or was created successfully, False otherwise.
    """
    try:
        resp = requests.get(f"{R_API_URL}/ls", timeout=R_API_TIMEOUT)
        resp.raise_for_status()
        objs = resp.json()
    except requests.RequestException:
        return False

    # Typical /ls returns a list of object names
    if isinstance(objs, list) and 'ravendb_conn' in objs:
        return True
    # Some implementations might return a dict with an objects list
    if isinstance(objs, dict):
        if 'ravendb_conn' in objs.get('objects', []) or 'ravendb_conn' in objs:
            return True

    # Not present: build DB connection code from DB_URI
    try:
        db_uri = None
        # Prefer flask config if available in request context
        try:
            db_uri = current_app.config.get('DB_URI')
        except RuntimeError:
            db_uri = None
        if not db_uri:
            db_uri = os.environ.get('DB_URI')
        if not db_uri:
            return False

        parsed = urlparse(db_uri)
        user = unquote(parsed.username) if parsed.username else ''
        password = unquote(parsed.password) if parsed.password else ''
        host = parsed.hostname or 'localhost'
        port = parsed.port or 5432
        dbname = parsed.path.lstrip('/') if parsed.path else ''

        # R code to create the connection object. Load only required packages.
        code = (
            'library(RPostgres)\n'
            'library(DBI)\n'
            'ravendb_conn <- dbConnect(RPostgres::Postgres(),\n'
            f'                     dbname = "{dbname}",\n'
            f'                     host = "{host}",\n'
            f'                     port = {port},\n'
            f'                     user = "{user}",\n'
            f'                     password = "{password}")'
        )

        resp = requests.post(f"{R_API_URL}/run", json={"code": code}, timeout=R_API_TIMEOUT)
        try:
            resp.raise_for_status()
            return True
        except requests.RequestException:
            return False
    except Exception:
        return False

# List objects in R workspace
@r_notebook_endpoint.route('/api/rnotebook/ls', methods=['GET'])
@jwt_required()
def r_ls():
    try:
        resp = requests.get(f"{R_API_URL}/ls", timeout=R_API_TIMEOUT)
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

# Run arbitrary R code
@r_notebook_endpoint.route('/api/rnotebook/run', methods=['POST'])
@jwt_required()
def r_run():
    # Make sure ravendb_conn exists in the R session before running arbitrary code
    if not ensure_ravendb_conn():
        return jsonify({"error": "Could not ensure ravendb_conn in R session"}), 500

    data = request.get_json(force=True)
    code = data.get('code', '')

    if not code:
        return jsonify({"error": "No code provided"}), 400
    try:
        resp = requests.post(f"{R_API_URL}/run", json={"code": code}, timeout=R_API_TIMEOUT)
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

# Reset R workspace
@r_notebook_endpoint.route('/api/rnotebook/reset', methods=['POST'])
@jwt_required()
def r_reset():
    try:
        resp = requests.post(f"{R_API_URL}/reset", timeout=R_API_TIMEOUT)
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

# Upload a file to R workspace
@r_notebook_endpoint.route('/api/rnotebook/files/upload', methods=['POST'])
@jwt_required()
def r_upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    try:
        resp = requests.post(f"{R_API_URL}/files/upload", files={'file': (file.filename, file.stream)}, timeout=R_API_TIMEOUT)
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

# Download a file from R workspace
@r_notebook_endpoint.route('/api/rnotebook/files/download', methods=['GET'])
@jwt_required()
def r_download_file():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "No file name provided"}), 400
    try:
        resp = requests.get(f"{R_API_URL}/files/download", params={"name": name}, timeout=R_API_TIMEOUT)
        resp.raise_for_status()
        return (resp.content, resp.status_code, resp.headers.items())
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


# Import a saved .R file into the R persistent session (.PERSIST_ENV)
@r_notebook_endpoint.route('/api/rnotebook/import', methods=['POST'])
@jwt_required()
def r_import_file():
    data = request.get_json(force=True)
    filename = data.get('filename')
    if not filename:
        return jsonify({"error": "No filename provided"}), 400

    # ensure file path is inside RFILES_DIR
    safe_path = os.path.join(RFILES_DIR, filename)
    if not os.path.isfile(safe_path):
        return jsonify({"error": "File not found"}), 404

    try:
        with open(safe_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return jsonify({"error": f"Could not read file: {str(e)}"}), 500

    if not content:
        return jsonify({"error": "Empty file"}), 400

    # Post the file content to the R API /run endpoint so it's evaluated in .PERSIST_ENV
    try:
        resp = requests.post(f"{R_API_URL}/run", json={"code": content}, timeout=R_API_TIMEOUT)
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500
    
@r_notebook_endpoint.route('/api/rnotebook/rfiles', methods=['GET'])
def list_rfiles():
    files = [f for f in os.listdir(RFILES_DIR) if f.endswith('.R')]
    return jsonify(files)

@r_notebook_endpoint.route('/api/rnotebook/rfiles/<filename>', methods=['GET'])
def get_rfile(filename):
    path = os.path.join(RFILES_DIR, filename)
    if not os.path.isfile(path):
        from flask import abort
        abort(404)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    return jsonify({'filename': filename, 'content': content})

@r_notebook_endpoint.route('/api/rnotebook/rfiles', methods=['POST'])
def save_rfile():
    data = request.get_json()
    filename = data.get('filename')
    content = data.get('content')
    if not filename or not content:
        from flask import abort
        abort(400)
    if not filename.endswith('.R'):
        filename += '.R'
    path = os.path.join(RFILES_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return jsonify({'success': True, 'filename': filename})

@r_notebook_endpoint.route('/api/rnotebook/rfiles/<filename>', methods=['PUT'])
def update_rfile(filename):
    data = request.get_json()
    content = data.get('content')
    if not content:
        from flask import abort
        abort(400)
    path = os.path.join(RFILES_DIR, filename)
    if not os.path.isfile(path):
        from flask import abort
        abort(404)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return jsonify({'success': True, 'filename': filename})

@r_notebook_endpoint.route('/api/rnotebook/rfiles/<filename>', methods=['DELETE'])
def delete_rfile(filename):
    path = os.path.join(RFILES_DIR, filename)
    if not os.path.isfile(path):
        from flask import abort
        abort(404)
    os.remove(path)
    return jsonify({'success': True, 'filename': filename})


def run_r_code(r_code: str) -> str:
    """Run R code using Rscript and return the output or errors."""
    import base64
    # Use RFILES_DIR for temp and output files
    temp_dir = RFILES_DIR
    os.makedirs(temp_dir, exist_ok=True)
    # Create a temporary R file in rfiles
    with tempfile.NamedTemporaryFile(mode='w', suffix='.R', dir=temp_dir, delete=False) as tmp:
        tmp.write(r_code)
        tmp_path = tmp.name

    before_files = set(os.listdir(temp_dir))

    result = {}
    try:
        process = subprocess.run(
            ["Rscript", tmp_path],
            capture_output=True,
            text=True,
            cwd=temp_dir
        )

        result["stdout"] = process.stdout
        result["stderr"] = process.stderr
        result["returncode"] = process.returncode

        # Find new files created by R in rfiles
        after_files = set(os.listdir(temp_dir))
        new_files = after_files - before_files
        for fname in new_files:
            fpath = os.path.join(temp_dir, fname)
            if fname.lower().endswith('.png') or fname.lower().endswith('.jpg'):
                with open(fpath, "rb") as img_file:
                    result["image"] = base64.b64encode(img_file.read()).decode("utf-8")
                os.remove(fpath)
            elif fname.lower().endswith('.csv'):
                with open(fpath, "r", encoding="utf-8") as csv_file:
                    result["csv"] = csv_file.read()
                os.remove(fpath)
            # Add more file types as needed
        return result
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@r_notebook_endpoint.route('/api/rnotebook/run_r', methods=['POST'])
@jwt_required()  # require auth
def run_r():
    data = request.get_json()

    if not data or "code" not in data:
        raise BadRequest("No R code provided.")

    r_code = data["code"]
    result = run_r_code(r_code)
    return jsonify(result)
