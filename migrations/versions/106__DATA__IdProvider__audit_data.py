from sqlalchemy import (
    MetaData,
    Table,
    select,
    update,
)


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    conn = migrate_engine.connect()

    idp = Table("id_provider", meta, autoload=True)

    for type in ['bioresource_id_provider', 'legacy_id_provider', 'pseudo_random_id_provider', 'sequential_id_provider']:
        inp = Table(type, meta, autoload=True)

        for id, last_updated_datetime, last_updated_by_user_id in conn.execute(select(inp.c.id_provider_id, inp.c.last_updated_datetime, inp.c.last_updated_by_user_id)):
            conn.execute(update(idp).where(idp.c.id_provider_id == id).values(last_updated_datetime=last_updated_datetime, last_updated_by_user_id=last_updated_by_user_id))


def downgrade(migrate_engine):
    pass