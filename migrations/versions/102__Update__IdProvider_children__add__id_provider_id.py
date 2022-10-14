from sqlalchemy import (
    Integer,
    MetaData,
    Table,
    Column,
    Index,
)
from sqlalchemy.schema import ForeignKeyConstraint


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    idp = Table("id_provider", meta, autoload=True)

    for type in ['bioresource_id_provider', 'legacy_id_provider', 'pseudo_random_id_provider', 'sequential_id_provider']:
        inp = Table(type, meta, autoload=True)

        id_provider_id = Column("id_provider_id", Integer, index=True)
        id_provider_id.create(inp, index_name=f'idx__{type}__id_provider_id')

        inp.append_constraint(ForeignKeyConstraint([id_provider_id], [idp.c.id_provider_id]))

def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    for type in ['bioresource_id_provider', 'legacy_id_provider', 'pseudo_random_id_provider', 'sequential_id_provider']:
    # for type in ['bioresource_id_provider']:
        inp = Table(type, meta, autoload=True)

        inp.c.id_provider_id.drop()
