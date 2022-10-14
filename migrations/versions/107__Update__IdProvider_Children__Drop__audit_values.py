from sqlalchemy import (
    MetaData,
    Table,
    Column,
    DateTime,
    Integer,
)


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    for type in ['bioresource_id_provider', 'legacy_id_provider', 'pseudo_random_id_provider', 'sequential_id_provider']:
        t = Table(type, meta, autoload=True)

        t.c.last_updated_by_user_id.drop()
        t.c.last_updated_datetime.drop()


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    for type in ['bioresource_id_provider', 'legacy_id_provider', 'pseudo_random_id_provider', 'sequential_id_provider']:
        t = Table(type, meta, autoload=True)

        last_updated_datetime = Column("last_updated_datetime", DateTime)
        last_updated_datetime.create(t)

        last_updated_by_user_id = Column("last_updated_by_user_id", Integer)
        last_updated_by_user_id.create(t)

