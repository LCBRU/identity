from sqlalchemy import (
    MetaData,
    Table,
)
from sqlalchemy import select, update

def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    conn = migrate_engine.connect()

    u = Table("user", meta, autoload=True)

    for type in ['bioresource_id', 'legacy_id', 'pseudo_random_id']:
        t = Table(type, meta, autoload=True)

        upd = update(t).values({
            t.c.last_update_date: t.c.last_updated_datetime,
            t.c.created_date: t.c.last_updated_datetime,
            t.c.last_update_by: select(u.c.username).where(u.c.id == t.c.last_updated_by_user_id).scalar_subquery(),
            t.c.created_by: select(u.c.username).where(u.c.id == t.c.last_updated_by_user_id).scalar_subquery(),
        })

    conn.execute(upd)

def downgrade(migrate_engine):
    pass