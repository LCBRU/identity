from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
)
from sqlalchemy.schema import ForeignKeyConstraint
from migrate.changeset.constraint import ForeignKeyConstraint as fkc

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    es = Table("ecrf_source", meta, autoload=True)
    s = Table("study", meta, autoload=True)

    t = Table("participant_import_definition", meta, autoload=True)

    t.append_constraint(ForeignKeyConstraint([t.c.ecrf_source_id], [es.c.id], name='fk__participant_import_definition__ecrf_source_id'))
    t.append_constraint(ForeignKeyConstraint([t.c.study_id], [s.c.id], name='fk__participant_import_definition__study_id'))


def downgrade(migrate_engine):
    meta.bind = migrate_engine

    es = Table("ecrf_source", meta, autoload=True)
    s = Table("study", meta, autoload=True)

    t = Table("participant_import_definition", meta, autoload=True)

    c1 = fkc([t.c.ecrf_source_id], [es.c.id])
    c1.drop()

    c1 = fkc([t.c.study_id], [s.c.id])
    c1.drop()

    pass