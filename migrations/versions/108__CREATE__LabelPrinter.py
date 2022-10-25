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

    t = Table(
        "label_printer",
        meta,
        Column("id", Integer, primary_key=True, nullable=False),
        Column("name", NVARCHAR(100), nullable=False),
        Column("hostname_or_ip_address", NVARCHAR(100), nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("label_printer", meta, autoload=True)
    t.drop()
