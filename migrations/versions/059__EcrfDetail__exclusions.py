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

    excluded_from_analysis = Column("excluded_from_analysis", DateTime)
    excluded_from_analysis.create(t)
    excluded_from_study = Column("excluded_from_study", DateTime)
    excluded_from_study.create(t)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("ecrf_detail", meta, autoload=True)
    t.c.excluded_from_analysis.drop()
    t.c.excluded_from_study.drop()
