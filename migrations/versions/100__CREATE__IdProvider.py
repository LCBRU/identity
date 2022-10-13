from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    ForeignKey,
    NVARCHAR,
    UnicodeText,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table(
        "id_provider",
        meta,
        Column("id", Integer, primary_key=True, nullable=False),
        Column("name", NVARCHAR(100), nullable=False),
        Column("prefix", NVARCHAR(10), nullable=True),
        Column("type", NVARCHAR(100), nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("id_provider", meta, autoload=True)
    t.drop()
