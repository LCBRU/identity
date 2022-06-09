import jsonschema
from functools import wraps
from flask import abort, current_app, request, jsonify
from .model import get_api_key


def assert_api_key():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if get_api_key(request) is None:
                current_app.logger.info(f'API Key not found or not supplied')
                abort(401)

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def validate_json(schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                jsonschema.validate(request.json, schema)
            except jsonschema.ValidationError as e:
                current_app.logger.info(f'JSON Validation errors: {e.message}')
                return jsonify(e.message), 400

            return f(*args, **kwargs)

        return decorated_function
    return decorator
