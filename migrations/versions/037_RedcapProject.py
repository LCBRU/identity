from sqlalchemy import (
    MetaData,
    Table,
    Column,
    NVARCHAR,
    Integer,
    NVARCHAR,
    ForeignKey,
    Date,
    DateTime,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    u = Table("user", meta, autoload=True)
    r = Table("redcap_instance", meta, autoload=True)
    s = Table("study", meta, autoload=True)

    t = Table(
        "redcap_project",
        meta,
        Column("id", Integer, primary_key=True),
        Column("name", NVARCHAR(100)),
        Column("project_id", Integer, index=True, nullable=False),
        Column("redcap_instance_id", Integer, ForeignKey(r.c.id), index=True, nullable=False),
        Column("study_id", Integer, ForeignKey(s.c.id), index=True),
        Column("last_updated_datetime", DateTime, nullable=False),
        Column("last_updated_by_user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("redcap_project", meta, autoload=True)
    t.drop()
