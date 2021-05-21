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
    conn = migrate_engine.connect()
    meta.bind = migrate_engine

    t = Table("participant_identifier_source", meta, autoload=True)

    upd = t.update().values(linked_minimum_patient_identifier_source_id=t.c.id)
    conn.execute(upd)


def downgrade(migrate_engine):
    pass
