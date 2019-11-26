from sqlalchemy import (
    MetaData,
    Table,
    Column,
    NVARCHAR,
    Integer,
    Index,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("sequential_id_provider", meta, autoload=True)

    prefix = Column("prefix", NVARCHAR(10), unique=True)
    prefix.create(t, unique_name="uq_sequential_id_provider_prefix")
    zero_fill_size = Column("zero_fill_size", Integer)
    zero_fill_size.create(t)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("sequential_id_provider", meta, autoload=True)
    t.c.prefix.drop()
    t.c.zero_fill_size.drop()
