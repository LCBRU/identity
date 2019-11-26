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

    t = Table(
        "pseudo_random_id_provider",
        meta,
        Column("id", Integer, primary_key=True),
        Column("name", NVARCHAR(100), index=True, unique=True, nullable=False),
        Column("prefix", NVARCHAR(100), unique=True, nullable=False),
        Column("last_updated_datetime", DateTime, nullable=False),
        Column("last_updated_by_user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
        UniqueConstraint(
            'name',
            name='uix_pseudo_random_id_provider_name'
        ),
        UniqueConstraint(
            'prefix',
            name='uix_pseudo_random_id_provider_prefix'
        ),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("pseudo_random_id_provider", meta, autoload=True)
    t.drop()