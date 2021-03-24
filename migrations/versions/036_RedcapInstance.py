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

    u = Table("user", meta, autoload=True)

    t = Table(
        "redcap_instance",
        meta,
        Column("id", Integer, primary_key=True),
        Column("name", NVARCHAR(100)),
        Column("database_name", NVARCHAR(100)),
        Column("base_url", NVARCHAR(500)),
        Column("last_updated_datetime", DateTime, nullable=False),
        Column("last_updated_by_user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("redcap_instance", meta, autoload=True)
    t.drop()
