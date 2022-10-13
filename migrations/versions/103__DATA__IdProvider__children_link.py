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

        for id, name in conn.execute(select(idp.c.id, idp.c.name).where(idp.c.type == type)):
            conn.execute(update(inp).where(inp.c.name == name).values(id_provider_id=id))


def downgrade(migrate_engine):
    pass