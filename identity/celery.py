from celery import Celery
from identity.config import IdentityConfig


celery = Celery(
    'Identity',
    broker=IdentityConfig.BROKER_URL,
    backend=IdentityConfig.CELERY_RESULT_BACKEND,
)

class Config():
    def __init__(self):
        self.broker_url = IdentityConfig.BROKER_URL
        self.result_backend = IdentityConfig.CELERY_RESULT_BACKEND
        self.task_default_rate_limit = IdentityConfig.CELERY_RATE_LIMIT
        self.worker_redirect_stdouts_level = IdentityConfig.CELERY_REDIRECT_STDOUTS_LEVEL
        self.task_default_queue = IdentityConfig.CELERY_DEFAULT_QUEUE



def init_celery(app):
    celery.config_from_object(Config())

    class ContextTask(celery.Task):
        rate_limit = app.config['CELERY_RATE_LIMIT']
        
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
