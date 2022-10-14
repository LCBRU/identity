from sqlalchemy import (
    NVARCHAR,
    MetaData,
    Table,
    Column,
)


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    for type in ['bioresource_id_provider', 'legacy_id_provider', 'pseudo_random_id_provider', 'sequential_id_provider']:
        t = Table(type, meta, autoload=True)

        t.c.name.drop()
        t.c.prefix.drop()


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    for type in ['bioresource_id_provider', 'legacy_id_provider', 'pseudo_random_id_provider', 'sequential_id_provider']:
        t = Table(type, meta, autoload=True)

        name = Column("name", NVARCHAR(100))
        name.create(t)

        prefix = Column("prefix", NVARCHAR(10))
        prefix.create(t)

