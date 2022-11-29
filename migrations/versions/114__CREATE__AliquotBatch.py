from sqlalchemy import (
    INTEGER,
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
    ForeignKey,
    Text,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    b = Table("label_bundle", meta, autoload=True)
    i = Table("id_provider", meta, autoload=True)

    t = Table(
        "aliquot_batch",
        meta,
        Column("id", Integer, primary_key=True, nullable=False),
        Column("label_bundle_id", Integer, ForeignKey(b.c.id), index=True, nullable=False),
        Column("id_provider_id", Integer, ForeignKey(i.c.id_provider_id), index=True, nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("aliquot_batch", meta, autoload=True)
    t.drop()
