from sqlalchemy import (
    Integer,
    MetaData,
    Table,
    Column,
    Index,
)
from sqlalchemy.schema import ForeignKeyConstraint


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    t = Table("blinding_type", meta, autoload=True)
    s = Table("study", meta, autoload=True)

    study_id = Column("study_id", Integer, index=True)
    study_id.create(t, index_name='idx__blinding_type__study_id')

    t.append_constraint(ForeignKeyConstraint([study_id], [s.c.id]))


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    t = Table("blinding_type", meta, autoload=True)

    t.c.study_id.drop()
