from sqlalchemy import create_engine
from contextlib import contextmanager
from flask import current_app
from sqlalchemy.orm import Session


@contextmanager
def pmi_engine():
    try:
        current_app.logger.info(f'Starting PMI engine')
        engine = create_engine(
            current_app.config['PMI_DB_URI'],
            echo=current_app.config['SQLALCHEMY_ECHO'],
        )
        yield engine.connect()
    finally:
        engine.dispose()
        current_app.logger.info(f'Disposing PMI engine')


@contextmanager
def civicrm_session():
    try:
        current_app.logger.info(f'Starting CiviCRM engine')
        engine = create_engine(
            current_app.config['CIVICRM_DB_URI'],
            echo=current_app.config['SQLALCHEMY_ECHO'],
        )
        with Session(engine) as session:
            yield session
    finally:
        engine.dispose()
        current_app.logger.info(f'Disposing CiviCRM engine')
