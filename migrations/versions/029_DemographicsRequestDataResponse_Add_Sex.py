from sqlalchemy import (
    MetaData,
    Table,
    Column,
    NVARCHAR,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("demographics_request_data_response", meta, autoload=True)

    sex = Column("sex", NVARCHAR(10))
    sex.create(t)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("demographics_request_data_response", meta, autoload=True)
    t.c.sex.drop()
