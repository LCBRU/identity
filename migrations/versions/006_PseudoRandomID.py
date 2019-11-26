from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
    DateTime,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)


meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    u = Table("user", meta, autoload=True)
    p = Table("pseudo_random_id_provider", meta, autoload=True)

    t = Table(
        "pseudo_random_id",
        meta,
        Column("id", Integer, primary_key=True),
        Column("pseudo_random_id_provider_id", Integer, ForeignKey(p.c.id), index=True, nullable=False),
        Column("ordinal", Integer),
        Column("unique_code", Integer),
        Column("check_character", NVARCHAR(1)),
        Column("full_code", NVARCHAR(20)),
        Column("last_updated_datetime", DateTime, nullable=False),
        Column("last_updated_by_user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
        UniqueConstraint(
            'pseudo_random_id_provider_id',
            'ordinal',
            name='uix_pseudo_random_id_pseudo_random_id_provider_id_ordinal'
        ),
        UniqueConstraint(
            'pseudo_random_id_provider_id',
            'unique_code',
            name='uix_pseudo_random_id_pseudo_random_id_provider_id_unique_code'
        ),
        UniqueConstraint(
            'full_code',
            name='uix_pseudo_random_id_full_code'
        ),
    )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("pseudo_random_id", meta, autoload=True)
    t.drop()
