from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
    ForeignKey,
    UniqueConstraint,
    DateTime,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    drd = Table("demographics_request_data", meta, autoload=True)

    t = Table(
        "demographics_request_data_message",
        meta,
        Column("id", Integer, primary_key=True),
        Column("demographics_request_data_id", Integer, ForeignKey(drd.c.id), index=True, nullable=False),
        Column("type", NVARCHAR(100)),
        Column("source", NVARCHAR(100)),
        Column("scope", NVARCHAR(100)),
        Column("message", NVARCHAR(500)),
        Column("created_datetime", DateTime),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("demographics_request_data_message", meta, autoload=True)
    t.drop()
