from sqlalchemy import (
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

    e = Table("participant_identifier", meta, autoload=True)
    p = Table("ecrf_detail", meta, autoload=True)

    t = Table(
        "ecrf_details__participant_identifiers",
        meta,
        Column("id", Integer, primary_key=True),
        Column("ecrf_detail_id", Integer, ForeignKey(e.c.id), index=True, nullable=False),
        Column("participant_identifier_id", Integer, ForeignKey(p.c.id), index=True, nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("ecrf_details__participant_identifiers", meta, autoload=True)
    t.drop()
