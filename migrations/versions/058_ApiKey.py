from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    ForeignKey,
    DateTime,
    NVARCHAR,
)
from sqlalchemy.schema import ForeignKeyConstraint

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    u = Table("user", meta, autoload=True)
    t = Table(
        "api_key",
        meta,
        Column("id", Integer, primary_key=True),
        Column("key", NVARCHAR(100), index=True, nullable=False),
        Column("user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("api_key", meta, autoload=True)
    t.drop()
