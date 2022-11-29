from sqlalchemy import (
    INTEGER,
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

    b = Table("label_bundle", meta, autoload=True)

    t = Table(
        "medical_notes_label",
        meta,
        Column("id", Integer, primary_key=True, nullable=False),
        Column("version_num", Integer, nullable=False),
        Column("label_bundle_id", Integer, ForeignKey(b.c.id), index=True, nullable=False),
        Column("study_name_line_1", NVARCHAR(100), nullable=False),
        Column("study_name_line_2", NVARCHAR(100), nullable=False),
        Column("chief_investigator", NVARCHAR(100), nullable=False),
        Column("chief_investigator_email", NVARCHAR(100), nullable=False),
        Column("study_sponsor", NVARCHAR(100), nullable=False),
        Column("iras_id", NVARCHAR(100), nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("medical_notes_label", meta, autoload=True)
    t.drop()
