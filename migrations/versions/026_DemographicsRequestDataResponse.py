from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
    ForeignKey,
    UniqueConstraint,
    UnicodeText,
    BOOLEAN,
    DATE,
    DateTime,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    drd = Table("demographics_request_data", meta, autoload=True)

    t = Table(
        "demographics_request_data_response",
        meta,
        Column("id", Integer, primary_key=True),
        Column("demographics_request_data_id", Integer, ForeignKey(drd.c.id), index=True, nullable=False),
        Column("title", NVARCHAR(100)),
        Column("forename", NVARCHAR(100)),
        Column("middlenames", NVARCHAR(200)),
        Column("lastname", NVARCHAR(100)),
        Column("postcode", NVARCHAR(50)),
        Column("address", UnicodeText),
        Column("date_of_birth", DATE),
        Column("date_of_death", DATE),
        Column("is_deceased", BOOLEAN),
        Column("current_gp_practice_code", NVARCHAR(50)),
        Column("created_datetime", DateTime),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("demographics_request_data_response", meta, autoload=True)
    t.drop()
