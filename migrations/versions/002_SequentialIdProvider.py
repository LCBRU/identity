from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
    DateTime,
    Boolean,
    ForeignKey,
)


meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    u = Table("user", meta, autoload=True)

    t = Table(
        "sequential_id_provider",
        meta,
        Column("id", Integer, primary_key=True),
        Column("name", NVARCHAR(100), index=True, nullable=False, unique=True),
        Column("last_number", Integer),
        Column("last_updated_datetime", DateTime, nullable=False),
        Column("last_updated_by_user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("sequential_id_provider", meta, autoload=True)
    t.drop()