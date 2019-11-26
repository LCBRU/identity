from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    u = Table("user", meta, autoload=True)

    t = Table(
        "role",
        meta,
        Column("id", Integer, primary_key=True),
        Column("name", NVARCHAR(100), nullable=False, index=True),
        Column("last_updated_datetime", DateTime, nullable=False),
        Column("last_updated_by_user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("role", meta, autoload=True)
    t.drop()
