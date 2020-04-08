from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    ForeignKey,
    DateTime,
)
from sqlalchemy.schema import ForeignKeyConstraint

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("ecrf_details__participant_identifiers", meta, autoload=True)
    t.drop()


def downgrade(migrate_engine):
    meta.bind = migrate_engine

    pass
