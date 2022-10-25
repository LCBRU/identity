from email.policy import default
from sqlalchemy import (
    Boolean,
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
    ForeignKey,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    p = Table("label_printer", meta, autoload=True)

    t = Table(
        "label_printer_set",
        meta,
        Column("id", Integer, primary_key=True, nullable=False),
        Column("name", NVARCHAR(100), nullable=False),
        Column("bag_printer_id", Integer, ForeignKey(p.c.id), index=True, nullable=False),
        Column("sample_printer_id", Integer, ForeignKey(p.c.id), index=True, nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("label_printer_set", meta, autoload=True)
    t.drop()
