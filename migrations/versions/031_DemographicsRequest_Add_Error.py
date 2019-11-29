from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Text,
    DateTime,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("demographics_request", meta, autoload=True)

    error_datetime = Column("error_datetime", DateTime)
    error_datetime.create(t)
    error_message = Column("error_message", Text)
    error_message.create(t)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("demographics_request", meta, autoload=True)
    t.c.error_datetime.drop()
    t.c.error_message.drop()
