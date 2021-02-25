from sqlalchemy import create_engine
from contextlib import contextmanager
from flask import current_app

from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
import uuid


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
            f"mysql://{current_app.config['REDCAP_USERNAME']}:{current_app.config['REDCAP_PASSWORD']}@{current_app.config['REDCAP_HOST']}/{database_name}",
            echo=current_app.config['SQLALCHEMY_ECHO'],
        )
        yield engine
    finally:
        engine.dispose()
        current_app.logger.info(f'Disposing REDCap engine for {database_name}')


# See https://docs.sqlalchemy.org/en/13/core/custom_types.html#backend-agnostic-guid-type
class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value