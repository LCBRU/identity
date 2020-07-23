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

    t = Table("participant_import_definition", meta, autoload=True)
    t.c.non_completion_reason_column_name.drop()
    t.c.name.drop()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("participant_import_definition", meta, autoload=True)

    non_completion_reason_column_name = Column("non_completion_reason_column_name", NVARCHAR(100))
    non_completion_reason_column_name.create(t)

    name = Column("name", NVARCHAR(100))
    name.create(t)
