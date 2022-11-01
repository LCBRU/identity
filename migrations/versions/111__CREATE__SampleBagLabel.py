from sqlalchemy import (
    BOOLEAN,
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

    l = Table("label_batch", meta, autoload=True)

    t = Table(
        "sample_bag_label",
        meta,
        Column("id", Integer, primary_key=True, nullable=False),
        Column("version_num", Integer, nullable=False),
        Column("label_batch_id", Integer, ForeignKey(l.c.id), index=True, nullable=False),
        Column("title", NVARCHAR(100), nullable=False),
        Column("visit", NVARCHAR(100), nullable=False),
        Column("subheaders", Text, nullable=False),
        Column("warnings", Text, nullable=False),
        Column("small_format", BOOLEAN, nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("sample_bag_label", meta, autoload=True)
    t.drop()
