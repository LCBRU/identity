from celery import Celery
from identity.config import BaseConfig


celery = Celery(
    'Identity',
    broker=BaseConfig.BROKER_URL,
    backend=BaseConfig.CELERY_RESULT_BACKEND,
)

class Config():
    def __init__(self):
        self.broker_url = BaseConfig.BROKER_URL
        self.result_backend = BaseConfig.CELERY_RESULT_BACKEND
        self.task_default_rate_limit = BaseConfig.CELERY_RATE_LIMIT
        self.worker_redirect_stdouts_level = BaseConfig.CELERY_REDIRECT_STDOUTS_LEVEL
        self.task_default_queue = BaseConfig.CELERY_DEFAULT_QUEUE



def init_celery(app):
    celery.config_from_object(Config())

    class ContextTask(celery.Task):
        rate_limit = app.config['CELERY_RATE_LIMIT']
        
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
