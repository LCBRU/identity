from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    ForeignKey,
    NVARCHAR,
    UnicodeText,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    e = Table("ecrf_source", meta, autoload=True)
    t = Table(
        "civicrm_ecrf_source",
        meta,
        Column("id", Integer, ForeignKey(e.c.id), primary_key=True, nullable=False),
        Column("case_type_id", Integer, nullable=False),
        Column("custom_tables", NVARCHAR(500)),
     )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("civicrm_ecrf_source", meta, autoload=True)
    t.drop()
