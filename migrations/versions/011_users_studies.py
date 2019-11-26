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

    s = Table("study", meta, autoload=True)
    u = Table("user", meta, autoload=True)

    t = Table(
        "users_studies",
        meta,
        Column("id", Integer, primary_key=True),
        Column("user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
        Column("study_id", Integer, ForeignKey(s.c.id), index=True, nullable=False),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("users_studies", meta, autoload=True)
    t.drop()
