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
    t.c.ecrf_source_id.drop()


def downgrade(migrate_engine):
    meta.bind = migrate_engine

    pass