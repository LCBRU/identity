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

    t = Table("participant_identifier", meta, autoload=True)

    t.c.type.drop()
    t.c.study_id.drop()


def downgrade(migrate_engine):
    meta.bind = migrate_engine

    pass
