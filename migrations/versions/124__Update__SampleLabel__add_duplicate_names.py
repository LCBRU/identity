from sqlalchemy import (
    UnicodeText,
    MetaData,
    Table,
    Column,
)


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    t = Table("sample_label", meta, autoload=True)

    duplicate_names = Column("duplicate_names", UnicodeText)
    duplicate_names.create(t)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    idp = Table("sample_label", meta, autoload=True)
    idp.c.duplicate_names.drop()
