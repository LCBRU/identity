from sqlalchemy import (
    Integer,
    MetaData,
    Table,
    Column,
    DateTime,
)
from sqlalchemy.schema import ForeignKeyConstraint


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    idp = Table("id_provider", meta, autoload=True)
    idp.c.last_updated_datetime.drop()
    idp.c.last_updated_by_user_id.drop()


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    idp = Table("id_provider", meta, autoload=True)
    u = Table("user", meta, autoload=True)

    last_updated_datetime = Column("last_updated_datetime", DateTime)
    last_updated_datetime.create(idp)

    last_updated_by_user_id = Column("last_updated_by_user_id", Integer, index=True)
    last_updated_by_user_id.create(idp, index_name=f'idx__id_provider__last_updated_by_user_id')

    idp.append_constraint(ForeignKeyConstraint([last_updated_by_user_id], [u.c.id]))
