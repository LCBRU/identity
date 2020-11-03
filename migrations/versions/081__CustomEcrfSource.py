from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    ForeignKey,
    NVARCHAR,
    UnicodeText,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    e = Table("ecrf_source", meta, autoload=True)
    t = Table(
        "custom_ecrf_source",
        meta,
        Column("id", Integer, ForeignKey(e.c.id), primary_key=True, nullable=False),
        Column("database_name", NVARCHAR(100)),
        Column("data_query", UnicodeText, nullable=False),
        Column("most_recent_timestamp_query", UnicodeText, nullable=False),
        Column("link", NVARCHAR(500), nullable=False),
     )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("custom_ecrf_source", meta, autoload=True)
    t.drop()
