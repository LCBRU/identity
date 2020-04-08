from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    ForeignKey,
    DateTime,
    NVARCHAR,
)
from sqlalchemy.schema import ForeignKeyConstraint

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    pis = Table("participant_identifier_source", meta, autoload=True)
    t = Table(
        "label_participant_identifier_source",
        meta,
        Column("participant_identifier_source_id", Integer, ForeignKey(pis.c.id), primary_key=True, index=True, nullable=False),
     )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("label_participant_identifier_source", meta, autoload=True)
    t.drop()
