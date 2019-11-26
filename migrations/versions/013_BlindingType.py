from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
    ForeignKey,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    bs = Table("blinding_set", meta, autoload=True)
    pridp = Table("pseudo_random_id_provider", meta, autoload=True)

    t = Table(
        "blinding_type",
        meta,
        Column("id", Integer, primary_key=True),
        Column("name", NVARCHAR(100), nullable=False),
        Column("blinding_set_id", Integer, ForeignKey(bs.c.id), index=True, nullable=False),
        Column("pseudo_random_id_provider_id", Integer, ForeignKey(pridp.c.id), index=True, nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("blinding_type", meta, autoload=True)
    t.drop()
