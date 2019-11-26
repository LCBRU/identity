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
    drc = Table("demographics_request_column", meta, autoload=True)

    t = Table(
        "demographics_request_column_definition",
        meta,
        Column("id", Integer, primary_key=True),
        Column("demographics_request_id", Integer, ForeignKey(dr.c.id), index=True, nullable=False, unique=True),
        Column("last_updated_datetime", DateTime, nullable=False),
        Column("last_updated_by_user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
        Column("nhs_number_column_id", Integer, ForeignKey(drc.c.id), index=True, unique=True),
        Column("family_name_column_id", Integer, ForeignKey(drc.c.id), index=True, unique=True),
        Column("given_name_column_id", Integer, ForeignKey(drc.c.id), index=True, unique=True),
        Column("gender_column_id", Integer, ForeignKey(drc.c.id), index=True, unique=True),
        Column("dob_column_id", Integer, ForeignKey(drc.c.id), index=True, unique=True),
        Column("postcode_column_id", Integer, ForeignKey(drc.c.id), index=True, unique=True),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("demographics_request_column_definition", meta, autoload=True)
    t.drop()
