from sqlalchemy import (
    MetaData,
    Table,
    Column,
    NVARCHAR,
    Integer,
    NVARCHAR,
    ForeignKey,
    Date,
    DateTime,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    drd = Table("demographics_request_data", meta, autoload=True)

    t = Table(
        "demographics_request_pmi_data",
        meta,
        Column("id", Integer, primary_key=True),
        Column("demographics_request_data_id", Integer, ForeignKey(drd.c.id), index=True, nullable=False),
        Column("uhl_system_number", NVARCHAR(50), nullable=False),
        Column("nhs_number", NVARCHAR(500)),
        Column("family_name", NVARCHAR(500)),
        Column("given_name", NVARCHAR(500)),
        Column("gender", NVARCHAR(500)),
        Column("date_of_birth",Date),
        Column("date_of_death", Date),
        Column("postcode", NVARCHAR(500)),
        Column("created_datetime", DateTime),
     )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("demographics_request_pmi_data", meta, autoload=True)
    t.drop()
