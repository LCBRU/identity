from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    ForeignKey,

)
from sqlalchemy.sql.schema import Column
from sqlalchemy import Index

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("participant_identifier_source", meta, autoload=True)

    idx = Index('idx__pis__linked_minimum_patient_identifier_source_id', t.c.linked_minimum_patient_identifier_source_id)
    idx.create(migrate_engine)


def downgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("participant_identifier_source", meta, autoload=True)

    idx = Index('idx__pis__linked_minimum_patient_identifier_source_id', t.c.linked_minimum_patient_identifier_source_id)
    idx.drop(migrate_engine)
