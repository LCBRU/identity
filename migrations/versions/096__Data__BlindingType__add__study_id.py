from sqlalchemy import (
    MetaData,
    Table,
)


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine
    conn = migrate_engine.connect()

    bt = Table("blinding_type", meta, autoload=True)
    bs = Table("blinding_set", meta, autoload=True)

    upd = bt.update()\
        .values(study_id=bs.c.study_id)\
        .where(bt.c.blinding_set_id == bs.c.id)

    conn.execute(upd)

def downgrade(migrate_engine):
    pass
