from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
    Index,
    ForeignKey,
)
from sqlalchemy.schema import ForeignKeyConstraint

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    s = Table("study", meta, autoload=True)
    t = Table("participant_identifier", meta, autoload=True)

    type = Column("type", NVARCHAR(100), index=True)
    type.create(t, index_name='idx_participant_identifier_type')

    study_id = Column("study_id", Integer, index=True)
    study_id.create(t, index_name='idx_participant_identifier_study_id')

    t.append_constraint(ForeignKeyConstraint([study_id], [s.c.id]))


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("participant_identifier", meta, autoload=True)
    t.c.type.drop()
    t.c.study_id.drop()
