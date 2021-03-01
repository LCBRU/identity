from functools import wraps
from flask import abort, current_app, request, jsonify
from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema
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


class JsonInputs(Inputs):
    def __init__(self, schema, request):
        self.json = [JsonSchema(schema=schema)]
        super().__init__(request)


def validate_json(schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            validator = JsonInputs(schema, request)

            if not validator.validate():
                current_app.logger.info(f'JSON Validation errors: {validator.errors}')
                return jsonify(validator.errors), 400

            return f(*args, **kwargs)

        return decorated_function
    return decorator
