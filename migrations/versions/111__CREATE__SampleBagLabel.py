from sqlalchemy import (
    BOOLEAN,
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
    ForeignKey,
    Text,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    l = Table("label_bundle", meta, autoload=True)

    t = Table(
        "sample_bag_label",
        meta,
        Column("id", Integer, primary_key=True, nullable=False),
        Column("version_num", Integer, nullable=False),
        Column("label_bundle_id", Integer, ForeignKey(l.c.id), index=True, nullable=False),
        Column("title", NVARCHAR(100), nullable=False),
        Column("visit", NVARCHAR(100), nullable=True),
        Column("subheaders", Text, nullable=True),
        Column("warnings", Text, nullable=True),
        Column("small_format", BOOLEAN, nullable=False),
        Column("form_date_text", NVARCHAR(100), nullable=True),
        Column("form_time_text", NVARCHAR(100), nullable=True),
        Column("form_emergency_text", NVARCHAR(100), nullable=True),
        Column("form_consent_a_text", NVARCHAR(100), nullable=True),
        Column("form_consent_b_text", NVARCHAR(100), nullable=True),
        Column("font_differential", Integer, nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("sample_bag_label", meta, autoload=True)
    t.drop()
