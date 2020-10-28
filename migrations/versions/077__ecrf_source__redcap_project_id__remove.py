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

    t = Table("ecrf_source", meta, autoload=True)
    t.c.redcap_project_id.drop()


def downgrade(migrate_engine):
    meta.bind = migrate_engine

    pass