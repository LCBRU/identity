from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    ForeignKey,
    DateTime,
    NVARCHAR,
    Boolean,
)
from sqlalchemy.schema import ForeignKeyConstraint

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("blinding_type", meta, autoload=True)

    deleted = Column("deleted", Boolean, default=False)
    deleted.create(t)
    duplicate_number = Column("duplicate_number", Integer, default=0)
    duplicate_number.create(t)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("blinding_type", meta, autoload=True)

    t.c.deleted.drop()
    t.c.duplicate_number.drop()
