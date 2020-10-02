from sqlalchemy import (
    MetaData,
    Table,
)
from migrate.changeset.constraint import UniqueConstraint

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("blinding_type", meta, autoload=True)

    cons = UniqueConstraint(t.c.blinding_set_id, t.c.name, t.c.duplicate_number)
    cons.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("blinding_type", meta, autoload=True)
    cons = UniqueConstraint(t.c.blinding_set_id, t.c.name, t.c.duplicate_number)
    cons.drop()
