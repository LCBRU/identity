from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
    BOOLEAN,
    ForeignKey,
    DateTime,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    u = Table("user", meta, autoload=True)

    t = Table(
        "demographics_request",
        meta,
        Column("id", Integer, primary_key=True),
        Column("created_datetime", DateTime, nullable=False),
        Column("owner_user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
        Column("filename", NVARCHAR(500), nullable=False),
        Column("extension", NVARCHAR(100), nullable=False),
        Column("last_updated_datetime", DateTime, nullable=False),
        Column("last_updated_by_user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("demographics_request", meta, autoload=True)
    t.drop()
