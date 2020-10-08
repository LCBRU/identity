from sqlalchemy import (
    MetaData,
    Table,
    Column,
    BOOLEAN,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    dr = Table("demographics_request", meta, autoload=True)

    skip_pmi = Column("skip_pmi", BOOLEAN)
    skip_pmi.create(dr)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("demographics_request", meta, autoload=True)
    t.c.skip_pmi.drop()
