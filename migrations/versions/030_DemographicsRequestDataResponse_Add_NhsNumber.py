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

    nhs_number = Column("nhs_number", NVARCHAR(50))
    nhs_number.create(t)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("demographics_request_data_response", meta, autoload=True)
    t.c.nhs_number.drop()
