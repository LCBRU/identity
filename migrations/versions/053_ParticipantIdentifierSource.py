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
    s = Table("study", meta, autoload=True)
    t = Table(
        "participant_identifier_source",
        meta,
        Column("id", Integer, primary_key=True),
        Column("type", NVARCHAR(100), index=True, nullable=False),
        Column("study_id", Integer, ForeignKey(s.c.id), index=True, nullable=False),

        Column("last_updated_datetime", DateTime, nullable=False),
        Column("last_updated_by_user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("participant_identifier_source", meta, autoload=True)
    t.drop()
