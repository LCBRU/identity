from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    ForeignKey,
    DateTime,
    NVARCHAR,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("redcap_project", meta, autoload=True)

    ecrf_source_id = Column("ecrf_source_id", Integer, unique=True)
    ecrf_source_id.create(t, unique_name='uix__redcap_project__ecrf_source_id')

    t.c.name.drop()
    t.c.last_updated_datetime.drop()
    t.c.last_updated_by_user_id.drop()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("redcap_project", meta, autoload=True)
    t.c.ecrf_source_id.drop()

    name = Column("name", NVARCHAR(100))
    name.create(t)

    last_updated_datetime = Column("last_updated_datetime", DateTime)
    last_updated_datetime.create(t)

    u = Table("user", meta, autoload=True)

    last_updated_by_user_id = Column("last_updated_by_user_id", Integer, ForeignKey(u.c.id), index=True)
    last_updated_by_user_id.create(t, index_name='uix__redcap_project__last_updated_by_user_id')
