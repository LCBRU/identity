from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("demographics_request_column_definition", meta, autoload=True)

    uhl_system_number_column_id = Column("uhl_system_number_column_id", Integer)
    uhl_system_number_column_id.create(t)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("demographics_request_column_definition", meta, autoload=True)
    t.c.uhl_system_number_column_id.drop()
