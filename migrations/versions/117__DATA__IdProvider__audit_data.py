from sqlalchemy import (
    MetaData,
    Table,
)
from sqlalchemy import select, update

def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    conn = migrate_engine.connect()

    i = Table("id_provider", meta, autoload=True)
    u = Table("user", meta, autoload=True)

    upd = update(i).values({
        i.c.last_update_date: i.c.last_updated_datetime,
        i.c.created_date: i.c.last_updated_datetime,
        i.c.last_update_by: select(u.c.username).where(u.c.id == i.c.last_updated_by_user_id).scalar_subquery(),
        i.c.created_by: select(u.c.username).where(u.c.id == i.c.last_updated_by_user_id).scalar_subquery(),
    })

    conn.execute(upd)

def downgrade(migrate_engine):
    pass