from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Index,
    NVARCHAR,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("redcap_instance", meta, autoload=True)

    version = Column("version", NVARCHAR(10))
    version.create(t)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("redcap_instance", meta, autoload=True)
    t.c.version.drop()
