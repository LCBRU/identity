from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    ForeignKey,
    DateTime,
)
from sqlalchemy.schema import ForeignKeyConstraint

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    sp = Table("study_participant", meta, autoload=True)
    pi = Table("participant_identifier", meta, autoload=True)
    s = Table("study", meta, autoload=True)

    t = Table(
        "study_participant__participant_identifiers",
        meta,
        Column("study_participant_id", Integer, ForeignKey(sp.c.id), primary_key=True, index=True, nullable=False),
        Column("participant_identifier_id", Integer, ForeignKey(pi.c.id), primary_key=True, index=True, nullable=False),
        Column("study_id", Integer, ForeignKey(s.c.id), primary_key=True, index=True, nullable=False),
        ForeignKeyConstraint(
            ['study_participant_id', 'study_id'],
            ['study_participant.id', 'study_participant.study_id'],       
        ),
        ForeignKeyConstraint(
            ['participant_identifier_id', 'study_id'],
            ['participant_identifier.id', 'participant_identifier.study_id'],       
        ),
     )
    t.create()

def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("study_participant__participant_identifiers", meta, autoload=True)
    t.drop()
