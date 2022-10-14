from flask import Flask
from identity.setup import setup_data

from identity.template_filters import init_template_filters
from .ui import blueprint as ui_blueprint
from .api import blueprint as api_blueprint
from .admin import init_admin
from .printing import init_printing
from .celery import init_celery
from .config import Config
from lbrc_flask import init_lbrc_flask, ReverseProxied
from lbrc_flask.security import init_security, Role
from .model.security import User


def create_app(config=Config):
    app = Flask(__name__)
    app.wsgi_app = ReverseProxied(app.wsgi_app)
    app.config.from_object(config)

    TITLE = 'Identity'

    with app.app_context():
        init_lbrc_flask(app, TITLE)

        init_security(app, user_class=User, role_class=Role)
        init_admin(app, TITLE)
        init_printing(app)
        init_celery(app)
        init_template_filters(app)

        setup_data()

    app.register_blueprint(ui_blueprint)
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
