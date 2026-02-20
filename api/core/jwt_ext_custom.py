from functools import wraps
from flask import jsonify, request

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import JWTManager
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError

from config import Config


def jwt_required_with_users_claim():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            return verify_claim("users", fn, *args, **kwargs)
        return decorator
    return wrapper


def jwt_required_with_allnetworks_claim():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            return verify_claim("allnetworks", fn, *args, **kwargs)
        return decorator
    return wrapper


def jwt_required_with_qualitycontrol_claim():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            return verify_claim("qualitycontrol", fn, *args, **kwargs)
        return decorator
    return wrapper


def jwt_required_with_processing_claim():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            return verify_claim("processing", fn, *args, **kwargs)
        return decorator
    return wrapper


def jwt_required_with_exporting_claim():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            return verify_claim("exporting", fn, *args, **kwargs)
        return decorator
    return wrapper


def jwt_required_with_data_claim():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            return verify_claim("data", fn, *args, **kwargs)
        return decorator
    return wrapper


def jwt_required_with_management_claim():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            return verify_claim("management", fn, *args, **kwargs)
        return decorator
    return wrapper


def verify_claim(claim, fn, *args, **kwargs):
    verify_jwt_in_request()
    claims = get_jwt()
    if claims[claim]:
        return fn(*args, **kwargs)
    else:
        return jsonify(msg="Access to this resource was denied"), 403


def get_name():
    verify_jwt_in_request()
    claims = get_jwt()
    return claims["name"]


def get_networks():
    verify_jwt_in_request()
    claims = get_jwt()
    return claims["networks"]


def can_see_all_networks():
    verify_jwt_in_request()
    claims = get_jwt()
    return claims["allnetworks"]


def api_key_or_jwt_required(*required_claims):
    """
    Decorator that accepts either API key (X-API-Key header) or JWT authentication.
    
    For API key authentication:
    - Checks X-API-Key header against PLANS_PROGRAMS_API_KEY from config
    - Grants full access (equivalent to management + allnetworks claims)
    
    For JWT authentication:
    - Falls back to standard JWT verification
    - Verifies all required claims are present and true
    
    Args:
        *required_claims: Variable number of claim names to verify (e.g., 'management', 'allnetworks')
    
    Example:
        @api_key_or_jwt_required('management', 'allnetworks')
        def my_route():
            return jsonify({"status": "ok"})
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Check for API key authentication first
            api_key = request.headers.get('X-API-Key')
            configured_key = Config.PLANS_PROGRAMS_API_KEY
            
            if api_key and configured_key:
                if api_key == configured_key:
                    # Valid API key - grant access
                    return fn(*args, **kwargs)
                else:
                    # Invalid API key
                    return jsonify({"msg": "Invalid API key"}), 401
            
            # No API key or not configured - fall back to JWT
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                
                # Verify all required claims
                for claim in required_claims:
                    if not claims.get(claim, False):
                        return jsonify(msg=f"Access denied: missing '{claim}' claim"), 403
                
                return fn(*args, **kwargs)
            
            except NoAuthorizationError:
                return jsonify({"msg": "Missing or invalid authentication (provide X-API-Key header or JWT token)"}), 401
            except Exception as e:
                return jsonify({"msg": f"Authentication error: {str(e)}"}), 401
        
        return decorator
    return wrapper
