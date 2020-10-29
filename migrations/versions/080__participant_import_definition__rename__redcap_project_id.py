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

    es = Table("ecrf_source", meta, autoload=True)

    t = Table("participant_import_definition", meta, autoload=True)
    t.c.redcap_project_id.drop()

    ecrf_source_id = Column("ecrf_source_id", Integer, index=True)
    ecrf_source_id.create(t, index_name='ix__participant_import_definition__ecrf_source_id')

    t.append_constraint(ForeignKeyConstraint([ecrf_source_id], [es.c.id], name='fk__participant_import_definition__ecrf_source_id'))


def downgrade(migrate_engine):
    meta.bind = migrate_engine

    pass