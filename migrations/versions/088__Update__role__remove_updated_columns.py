from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    DateTime,
)
from sqlalchemy.sql.schema import Column
from migrate.changeset.constraint import ForeignKeyConstraint

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("role", meta, autoload=True)
    u = Table("user", meta, autoload=True)

    cons = ForeignKeyConstraint([t.c.last_updated_by_user_id], [u.c.id])
    cons.drop()

    t.c.last_updated_datetime.drop()
    t.c.last_updated_by_user_id.drop()


def downgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("role", meta, autoload=True)
    u = Table("user", meta, autoload=True)

    last_updated_datetime = Column("last_updated_datetime", DateTime)
    last_updated_datetime.create(t)
    last_updated_by_user_id = Column("last_updated_by_user_id", Integer)
    last_updated_by_user_id.create(t)
