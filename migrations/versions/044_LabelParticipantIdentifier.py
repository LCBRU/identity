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

    pi = Table("participant_identifier", meta, autoload=True)

    t = Table(
        "label_participant_identifier",
        meta,
        Column("id", Integer, ForeignKey(pi.c.id), primary_key=True),
     )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("label_participant_identifier", meta, autoload=True)
    t.drop()
