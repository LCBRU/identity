from functools import wraps
from flask import abort
from flask_login import current_user
from lbrc_flask.database import db

from identity.printing import LabelBundle
from ..model import Study


def assert_study_user():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_admin:
                study_id = kwargs.get('id') or kwargs.get('study_id')
                study = Study.query.get_or_404(study_id)

                if study not in current_user.studies:
                    abort(403)

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def assert_can_print_study_label():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_admin:
                id = kwargs.get('id')
                bundle = db.get_or_404(LabelBundle, id)

                if bundle.study not in current_user.studies:
                    abort(403)

            return f(*args, **kwargs)

        return decorated_function
    return decorator
