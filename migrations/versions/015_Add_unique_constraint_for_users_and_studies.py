from sqlalchemy import (
    MetaData,
    Table,
)
from migrate.changeset.constraint import UniqueConstraint

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("users_studies", meta, autoload=True)

    cons = UniqueConstraint(t.c.user_id, t.c.study_id)
    cons.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("users_studies", meta, autoload=True)
    cons = UniqueConstraint(t.c.user_id, t.c.study_id)
    cons.drop()
