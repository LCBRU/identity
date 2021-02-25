from flask import Flask
from .ui import blueprint as ui_blueprint
from .security_ui import blueprint as security_ui_blueprint
from .api import blueprint as api_blueprint
from .security import init_security, init_users
from .admin import init_admin
from .printing import init_printing
from .setup import import_ids, create_base_data
from .utils import ReverseProxied
from .celery import init_celery
from .config import Config
from .ecrfs import init_redcap
from lbrc_flask import init_lbrc_flask


def create_app(config=Config):
    app = Flask(__name__)
    app.wsgi_app = ReverseProxied(app.wsgi_app)
    app.config.from_object(config)

    TITLE = 'Identity'

    with app.app_context():
        init_lbrc_flask(app, TITLE)

        init_security(app)
        init_admin(app)
        init_printing(app)
        init_celery(app)
        init_redcap(app)

    app.register_blueprint(security_ui_blueprint)
    app.register_blueprint(ui_blueprint)
    app.register_blueprint(api_blueprint, url_prefix='/api')


    @app.before_first_request
    def init_data():
        init_users()
        create_base_data()
        if not app.config['TESTING'] and app.config['IMPORT_OLD_IDS']:
            import_ids()

    return app
