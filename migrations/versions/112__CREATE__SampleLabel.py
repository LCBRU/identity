from sqlalchemy import (
    INTEGER,
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
    ForeignKey,
    BOOLEAN,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    l = Table("sample_bag_label", meta, autoload=True)
    i = Table("id_provider", meta, autoload=True)

    t = Table(
        "sample_label",
        meta,
        Column("id", Integer, primary_key=True, nullable=False),
        Column("sample_bag_label_id", Integer, ForeignKey(l.c.id), index=True, nullable=False),
        Column("id_provider_id", Integer, ForeignKey(i.c.id_provider_id), index=True, nullable=False),
        Column("name", NVARCHAR(100), nullable=False),
        Column("count", INTEGER, nullable=False),
        Column("duplicates", INTEGER, nullable=False),
        Column("print_on_bag", BOOLEAN, nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("sample_label", meta, autoload=True)
    t.drop()
