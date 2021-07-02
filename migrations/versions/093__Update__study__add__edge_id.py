from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
)
from sqlalchemy import Index


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    t = Table("study", meta, autoload=True)

    edge_id = Column("edge_id", Integer)
    edge_id.create(t)

    idx = Index('ix__study__edge_id', t.c.edge_id)
    idx.create(migrate_engine)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    t = Table("study", meta, autoload=True)

    t.c.edge_id.drop()

