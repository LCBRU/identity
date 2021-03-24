from sqlalchemy import (
    MetaData,
    Table,
    Column,
    NVARCHAR,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table(
        "participant_import_strategy",
        meta,
        Column("id", Integer, primary_key=True),
        Column("type", NVARCHAR(100), index=True, nullable=False, unique=True),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("participant_import_strategy", meta, autoload=True)
    t.drop()
