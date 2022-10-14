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

    l = Table("label_batch_set", meta, autoload=True)

    t = Table(
        "sample_label",
        meta,
        Column("id", Integer, primary_key=True, nullable=False),
        Column("label_batch_set_id", Integer, ForeignKey(l.c.id), index=True, nullable=False),
        Column("name", NVARCHAR(100), nullable=False),
        Column("count", INTEGER, nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("sample_label", meta, autoload=True)
    t.drop()
