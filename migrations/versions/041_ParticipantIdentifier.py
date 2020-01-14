from sqlalchemy import (
    MetaData,
    Table,
    Column,
    NVARCHAR,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    u = Table("user", meta, autoload=True)
    it = Table("participant_identifier_type", meta, autoload=True)

    t = Table(
        "participant_identifier",
        meta,
        Column("id", Integer, primary_key=True),
        Column("identifier", NVARCHAR(100), index=True, nullable=False),
        Column("participant_identifier_type_id", Integer, ForeignKey(it.c.id), index=True, nullable=False),

        Column("last_updated_datetime", DateTime, nullable=False),
        Column("last_updated_by_user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
        UniqueConstraint(
            'participant_identifier_type_id',
            'identifier',
            name='uix__participant_identifier__participant_identifier_type_id__identifier',
        )
     )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("participant_identifier", meta, autoload=True)
    t.drop()
