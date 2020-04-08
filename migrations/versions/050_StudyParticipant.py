from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    ForeignKey,
    DateTime,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    u = Table("user", meta, autoload=True)
    t = Table(
        "study_participant",
        meta,
        Column("id", Integer, primary_key=True),
        Column("study_id", Integer, index=True, nullable=False),

        Column("last_updated_datetime", DateTime, nullable=False),
        Column("last_updated_by_user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
     )
    t.create()

def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("study_participant", meta, autoload=True)
    t.drop()
