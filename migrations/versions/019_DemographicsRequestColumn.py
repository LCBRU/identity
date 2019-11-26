from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
    BOOLEAN,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    u = Table("user", meta, autoload=True)
    dr = Table("demographics_request", meta, autoload=True)

    t = Table(
        "demographics_request_column",
        meta,
        Column("id", Integer, primary_key=True),
        Column("demographics_request_id", Integer, ForeignKey(dr.c.id), index=True, nullable=False),
        Column("name", NVARCHAR(500), nullable=False),
        Column("last_updated_datetime", DateTime, nullable=False),
        Column("last_updated_by_user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
        UniqueConstraint('demographics_request_id', 'name', name='uix_demographics_request_column_demographics_request_id_name'),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("demographics_request_column", meta, autoload=True)
    t.drop()
