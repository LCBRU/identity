from sqlalchemy import (
    MetaData,
    Table,
    delete,
    insert,
    select,
    text,
)


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    conn = migrate_engine.connect()

    idp = Table("id_provider", meta, autoload=True)

    for type in ['bioresource_id_provider', 'legacy_id_provider', 'pseudo_random_id_provider', 'sequential_id_provider']:
        inp = Table(type, meta, autoload=True)

        sel = select(inp.c.name, inp.c.prefix, text(f"'{type}'"))
        ins = insert(idp).from_select([idp.c.name, idp.c.prefix, idp.c.type], sel)

        conn.execute(ins)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    conn = migrate_engine.connect()

    idp = Table("id_provider", meta, autoload=True)

    conn.execute(delete(idp))
