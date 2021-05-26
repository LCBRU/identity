from sqlalchemy import create_engine
from contextlib import contextmanager
from flask import current_app


@contextmanager
def pmi_engine():
    try:
        current_app.logger.info(f'Starting PMI engine')
        engine = create_engine(
            # f"mssql+pyodbc:///?odbc_connect={con_string}",
            current_app.config['PMI_DB_URI'],
            echo=current_app.config['SQLALCHEMY_ECHO'],
        )
        yield engine
    finally:
        engine.dispose()
        current_app.logger.info(f'Disposing PMI engine')


@contextmanager
def redcap_engine(database_name):
    try:
        current_app.logger.info(f'Starting REDCap engine for {database_name}')
        engine = create_engine(
            f"mysql+pymysql://{current_app.config['REDCAP_USERNAME']}:{current_app.config['REDCAP_PASSWORD']}@{current_app.config['REDCAP_HOST']}/{database_name}",
            echo=current_app.config['SQLALCHEMY_ECHO'],
        )
        yield engine
    finally:
        engine.dispose()
        current_app.logger.info(f'Disposing REDCap engine for {database_name}')
