from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
    ForeignKey,
    UniqueConstraint,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    dr = Table("demographics_request", meta, autoload=True)

    t = Table(
        "demographics_request_data",
        meta,
        Column("id", Integer, primary_key=True),
        Column("demographics_request_id", Integer, ForeignKey(dr.c.id), index=True, nullable=False),
        Column("row_number", Integer, nullable=False),
        Column("nhs_number", NVARCHAR(500)),
        Column("family_name", NVARCHAR(500)),
        Column("given_name", NVARCHAR(500)),
        Column("gender", NVARCHAR(500)),
        Column("dob", NVARCHAR(500)),
        Column("postcode", NVARCHAR(500)),
        UniqueConstraint('demographics_request_id', 'row_number', name='uix__demographics_request_id__row_number')
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("demographics_request_data", meta, autoload=True)
    t.drop()
