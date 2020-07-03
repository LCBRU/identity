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

    t = Table("ecrf_detail", meta, autoload=True)

    withdrawn_from_study = Column("withdrawn_from_study", DateTime)
    withdrawn_from_study.create(t)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("ecrf_detail", meta, autoload=True)
    t.c.withdrawn_from_study.drop()
