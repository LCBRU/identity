from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
    ForeignKey,
)
from sqlalchemy.schema import ForeignKeyConstraint

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    pis = Table("participant_import_strategy", meta, autoload=True)
    t = Table("redcap_project", meta, autoload=True)

    participant_import_strategy_id = Column("participant_import_strategy_id", Integer, index=True)
    participant_import_strategy_id.create(t, index_name='idx__redcap_project__pis_id')

    t.append_constraint(ForeignKeyConstraint([participant_import_strategy_id], [pis.c.id]))


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("redcap_project", meta, autoload=True)
    t.c.participant_import_strategy_id.drop()