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

    t = Table("redcap_project", meta, autoload=True)
    e = Table("ecrf_source", meta, autoload=True)

    t.append_constraint(ForeignKeyConstraint([t.c.ecrf_source_id], [e.c.id], name='fk__redcap_project__ecrf_source_id'))


def downgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("redcap_project", meta, autoload=True)
    e = Table("ecrf_source", meta, autoload=True)

    con = ForeignKeyConstraint([t.c.ecrf_source_id], [e.c.id], name='fk__redcap_project__ecrf_source_id')
    con.drop()
