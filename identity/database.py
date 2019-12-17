from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine
from contextlib import contextmanager
from flask import current_app


db = SQLAlchemy()


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
