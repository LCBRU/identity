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

    s = Table("study", meta, autoload=True)
    i = Table("id_provider", meta, autoload=True)
    p = Table("label_printer_set", meta, autoload=True)

    t = Table(
        "label_bundle",
        meta,
        Column("id", Integer, primary_key=True, nullable=False),
        Column("name", NVARCHAR(100), nullable=False),
        Column("study_id", Integer, ForeignKey(s.c.id), index=True, nullable=False),
        Column("participant_id_provider_id", Integer, ForeignKey(i.c.id_provider_id), index=True, nullable=False),
        Column("label_printer_set_id", Integer, ForeignKey(p.c.id), index=True, nullable=False),
        Column("disable_batch_printing", Boolean, nullable=False, default=False),
        Column("user_defined_participant_id", Boolean, nullable=False, default=False),
        Column("participant_label_count", Integer, nullable=False, default=False),
        Column("sidebar_prefix", NVARCHAR(100), nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("label_bundle", meta, autoload=True)
    t.drop()
