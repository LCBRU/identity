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
    t.c.non_completion_reason.drop()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("ecrf_detail", meta, autoload=True)

    non_completion_reason_column_name = Column("non_completion_reason", Integer)
    non_completion_reason_column_name.create(t)
