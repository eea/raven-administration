from flask import jsonify, Blueprint
from datetime import datetime

health_endpoint = Blueprint('health', __name__)


@health_endpoint.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint - no authentication required.
    Returns application status and timestamp.
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "raven-api"
    }), 200
