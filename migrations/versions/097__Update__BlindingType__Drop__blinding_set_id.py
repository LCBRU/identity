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

    t.c.blinding_set_id.drop()


def downgrade(migrate_engine):
    pass
