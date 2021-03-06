from sqlalchemy import (
    MetaData,
    Table,
    Column,
    NVARCHAR,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("role", meta, autoload=True)

    description = Column("description", NVARCHAR(255))
    description.create(t)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("role", meta, autoload=True)

    t.c.description.drop()
