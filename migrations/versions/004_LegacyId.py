from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
    DateTime,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)


meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    u = Table("user", meta, autoload=True)
    p = Table("legacy_id_provider", meta, autoload=True)

    t = Table(
        "legacy_id",
        meta,
        Column("id", Integer, primary_key=True),
        Column("legacy_id_provider_id", Integer, ForeignKey(p.c.id), index=True, nullable=False),
        Column("number", Integer),
        Column("last_updated_datetime", DateTime, nullable=False),
        Column("last_updated_by_user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
        UniqueConstraint('legacy_id_provider_id', 'number', name='uix_legacy_id_legacy_id_provider_id_number')
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("legacy_id", meta, autoload=True)
    t.drop()