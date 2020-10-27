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
        "ecrf_source",
        meta,
        Column("id", Integer, primary_key=True),
        Column("redcap_project_id", Integer),
        Column("type", NVARCHAR(100), index=True, nullable=False),
        Column("name", NVARCHAR(100), index=True, nullable=False),
        Column("last_updated_datetime", DateTime, nullable=False),
        Column("last_updated_by_user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
     )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("ecrf_source", meta, autoload=True)
    t.drop()
