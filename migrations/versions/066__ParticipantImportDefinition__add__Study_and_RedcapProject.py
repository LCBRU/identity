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

    rp = Table("redcap_project", meta, autoload=True)
    s = Table("study", meta, autoload=True)

    t = Table("participant_import_definition", meta, autoload=True)

    redcap_project_id = Column("redcap_project_id", Integer, index=True)
    redcap_project_id.create(t, index_name='idx__participant_import_definition__redcap_project_id')

    study_id = Column("study_id", Integer, index=True)
    study_id.create(t, index_name='idx__participant_import_definition__study_id')

    t.append_constraint(ForeignKeyConstraint([redcap_project_id], [rp.c.id]))
    t.append_constraint(ForeignKeyConstraint([study_id], [s.c.id]))


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("participant_import_definition", meta, autoload=True)

    t.c.redcap_project_id.drop()
    t.c.study_id.drop()
