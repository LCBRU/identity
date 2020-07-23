from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
)
from sqlalchemy.schema import ForeignKeyConstraint

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("redcap_project", meta, autoload=True)
    t.c.participant_import_definition_id.drop()
    t.c.study_id.drop()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    pid = Table("participant_import_definition", meta, autoload=True)
    s = Table("study", meta, autoload=True)

    t = Table("redcap_project", meta, autoload=True)

    participant_import_definition_id = Column("participant_import_definition_id", Integer, index=True)
    participant_import_definition_id.create(t, index_name='idx__redcap_project__pid_id')

    t.append_constraint(ForeignKeyConstraint([participant_import_definition_id], [pid.c.id]))

    study_id = Column("study_id", Integer, index=True)
    study_id.create(t, index_name='idx__redcap_project__study_id')

    t.append_constraint(ForeignKeyConstraint([participant_import_definition_id], [pid.c.id]))
    t.append_constraint(ForeignKeyConstraint([study_id], [s.c.id]))
