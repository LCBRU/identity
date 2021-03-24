from sqlalchemy import (
    MetaData,
    Table,
    Column,
    NVARCHAR,
    Integer,
    DateTime,
    ForeignKey,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    u = Table("user", meta, autoload=True)

    t = Table(
        "participant_identifier_type",
        meta,
        Column("id", Integer, primary_key=True),
        Column("name", NVARCHAR(100), index=True, unique=True, nullable=False),

        Column("last_updated_datetime", DateTime, nullable=False),
        Column("last_updated_by_user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("participant_identifier_type", meta, autoload=True)
    t.drop()
