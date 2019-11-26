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

    s = Table("study", meta, autoload=True)

    t = Table(
        "label_pack",
        meta,
        Column("id", Integer, primary_key=True),
        Column("type", NVARCHAR(100), nullable=False),
        Column("study_id", Integer, ForeignKey(s.c.id), index=True, nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("label_pack", meta, autoload=True)
    t.drop()
