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

    linked_minimum_patient_identifier_source_id = Column("linked_minimum_patient_identifier_source_id", Integer, ForeignKey(t.c.id))
    linked_minimum_patient_identifier_source_id.create(t)



def downgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("participant_identifier_source", meta, autoload=True)

    t.c.linked_minimum_patient_identifier_source_id.drop()

