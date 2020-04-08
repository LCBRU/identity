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

    pi = Table("participant_identifier", meta, autoload=True)
    pis = Table("participant_identifier_source", meta, autoload=True)
    t = Table(
        "participant_identifiers__participant_identifier_sources",
        meta,
        Column("participant_identifier_id", Integer, ForeignKey(pi.c.id), primary_key=True, index=True, nullable=False),
        Column("participant_identifier_source_id", Integer, ForeignKey(pis.c.id), primary_key=True, index=True, nullable=False),
     )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("participant_identifiers__participant_identifier_sources", meta, autoload=True)
    t.drop()
