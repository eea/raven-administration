from functools import wraps
from flask import jsonify

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import JWTManager
from flask_jwt_extended import verify_jwt_in_request


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


def jwt_required_with_observations_claim():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            return verify_claim("observations", fn, *args, **kwargs)
        return decorator
    return wrapper


def jwt_required_with_network_claim():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            return verify_claim("network", fn, *args, **kwargs)
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
