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

    rp = Table("redcap_project", meta, autoload=True)
    t = Table("ecrf_detail", meta, autoload=True)

    t.c.project_id.drop()

    redcap_project_id = Column("redcap_project_id", Integer, index=True)
    redcap_project_id.create(t, index_name='idx__ecrf_detail__redcap_project_id')

    t.append_constraint(ForeignKeyConstraint([redcap_project_id], [rp.c.id]))


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("ecrf_detail", meta, autoload=True)
    t.c.redcap_project_id.drop()
