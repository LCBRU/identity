from functools import wraps
from flask import abort
from flask_login import (
    LoginManager,
    current_user,
)

login_manager = LoginManager()


def must_be_admin():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_admin:
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator

