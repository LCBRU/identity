from sqlalchemy import (
    MetaData,
    Table,
    Column,
    NVARCHAR,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("demographics_request_data", meta, autoload=True)

    uhl_system_number = Column("uhl_system_number", NVARCHAR(50))
    uhl_system_number.create(t)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("demographics_request_data", meta, autoload=True)
    t.c.uhl_system_number.drop()