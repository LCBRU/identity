from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    bt = Table("blinding_type", meta, autoload=True)
    prid = Table("pseudo_random_id", meta, autoload=True)
    u = Table("user", meta, autoload=True)

    t = Table(
        "blinding",
        meta,
        Column("id", Integer, primary_key=True),
        Column("unblind_id", NVARCHAR(100), nullable=False),
        Column("blinding_type_id", Integer, ForeignKey(bt.c.id), index=True, nullable=False),
        Column("pseudo_random_id_id", Integer, ForeignKey(prid.c.id), index=True, nullable=False, unique=True),
        Column("last_updated_datetime", DateTime, nullable=False),
        Column("last_updated_by_user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
        UniqueConstraint(
            'blinding_type_id',
            'unblind_id',
            name='uix_blinding_blinding_type_id_unblind_id'
        ),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("blinding", meta, autoload=True)
    t.drop()
