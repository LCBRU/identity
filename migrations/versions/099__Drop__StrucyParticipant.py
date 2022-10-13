from sqlalchemy import (
    MetaData,
    Table,
)
from sqlalchemy.schema import ForeignKeyConstraint


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    t = Table("study_participant", meta, autoload=True)

    t.drop()


def downgrade(migrate_engine):
    pass
