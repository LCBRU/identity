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

    b = Table("aliquot_batch", meta, autoload=True)

    t = Table(
        "aliquot_label",
        meta,
        Column("id", Integer, primary_key=True, nullable=False),
        Column("aliquot_batch_id", Integer, ForeignKey(b.c.id), index=True, nullable=False),
        Column("prefix", NVARCHAR(100), nullable=False),
        Column("count", INTEGER, nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("aliquot_label", meta, autoload=True)
    t.drop()
