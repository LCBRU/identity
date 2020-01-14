from sqlalchemy import (
    MetaData,
    Table,
    UniqueConstraint,
)
from migrate.changeset.constraint import UniqueConstraint
from sqlalchemy.schema import DropConstraint

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    # drc = Table("demographics_request_column", meta, autoload=True)
    # migrate_engine.execute(DropConstraint(UniqueConstraint(
    #     drc.c.demographics_request_id,
    #     drc.c.name,
    #     name='uix_demographics_request_column_demographics_request_id_name',
    # )))


def downgrade(migrate_engine):
    meta.bind = migrate_engine

    # drc = Table("demographics_request_column", meta, autoload=True)

    # u = UniqueConstraint('demographics_request_id', 'name', table=drc)
    # u.create()
