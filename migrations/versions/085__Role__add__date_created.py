from sqlalchemy import (
    MetaData,
    Table,
    Column,
    DateTime,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("role", meta, autoload=True)

    date_created = Column("date_created", DateTime)
    date_created.create(t)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("role", meta, autoload=True)

    t.c.date_created.drop()
