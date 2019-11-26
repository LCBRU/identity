from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table(
        "study",
        meta,
        Column("id", Integer, primary_key=True),
        Column("name", NVARCHAR(50), nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("study", meta, autoload=True)
    t.drop()
