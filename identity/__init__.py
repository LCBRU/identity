import os
import traceback
import logging
from flask import Flask
from .ui import blueprint as ui_blueprint
from .security_ui import blueprint as security_ui_blueprint
from .database import db
from .template_filters import init_template_filters
from .standard_views import init_standard_views
from .emailing import init_mail
from .security import init_security, init_users
from .admin import init_admin
from .printing import init_printing
from .setup import import_ids, create_base_data
from .utils import ReverseProxied
from .celery import init_celery, celery
from .config import BaseConfig
from .redcap_import import *

def create_app(config=BaseConfig):
    app = Flask(__name__)
    app.wsgi_app = ReverseProxied(app.wsgi_app)
    app.config.from_object(config)
    app.config.from_pyfile("application.cfg", silent=True)

    with app.app_context():
        app.logger.setLevel(logging.INFO)
        db.init_app(app)
        init_mail(app)
        init_template_filters(app)
        init_standard_views(app)
        init_security(app)
        init_admin(app)
        init_printing(app)
        init_celery(app)

    app.register_blueprint(security_ui_blueprint)
    app.register_blueprint(ui_blueprint)

    @app.before_first_request
    def init_data():
        init_users()
        create_base_data()
        if not app.config['TESTING'] and app.config['IMPORT_OLD_IDS']:
            import_ids()

    return app
