from celery import Celery
from identity.config import BaseConfig


celery = Celery(
    'Identity',
    broker=BaseConfig.broker_url,
    backend=BaseConfig.result_backend,
)

def init_celery(app):
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        rate_limit = app.config['CELERY_RATE_LIMIT']
        
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
