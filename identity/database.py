from sqlalchemy import create_engine
from contextlib import contextmanager
from flask import current_app


@contextmanager
def pmi_engine():
    try:
        current_app.logger.info(f'Starting PMI engine')
        current_app.logger.warning(current_app.config['PMI_DB_URI'])
        engine = create_engine(
            current_app.config['PMI_DB_URI'],
            echo=current_app.config['SQLALCHEMY_ECHO'],
        )
        yield engine
    finally:
        engine.dispose()
        current_app.logger.info(f'Disposing PMI engine')
