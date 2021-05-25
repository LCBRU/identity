from sqlalchemy import (
    MetaData,
    Table,
    Column,
    BOOLEAN,
)

def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    t = Table("participant_import_definition", meta, autoload=True)

    active = Column("active", BOOLEAN, default=False)
    active.create(t)

    t.c.active.alter(nullable=False)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    t = Table("participant_import_definition", meta, autoload=True)

    t.c.active.drop()

