from sqlalchemy import (
    MetaData,
    Table,
    Column,
    NVARCHAR,
    Integer,
    NVARCHAR,
    ForeignKey,
    Date,
    DateTime,
    Boolean,
    UniqueConstraint,
    BigInteger,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    u = Table("user", meta, autoload=True)
    rp = Table("redcap_project", meta, autoload=True)

    t = Table(
        "ecrf_detail",
        meta,
        Column("id", Integer, primary_key=True),
        Column("project_id", Integer, ForeignKey(rp.c.id), index=True, nullable=False),
        Column("ecrf_participant_identifier", NVARCHAR(100), index=True, nullable=False),
        Column("recruitment_date", Date),
        Column("first_name", NVARCHAR(100)),
        Column("last_name", NVARCHAR(100)),
        Column("sex", NVARCHAR(1)),
        Column("postcode", NVARCHAR(10)),
        Column("birth_date", Date),
        Column("complete_or_expected", Boolean),
        Column("non_completion_reason", Integer),
        Column("withdrawal_date", Date),
        Column("post_withdrawal_keep_samples", Boolean),
        Column("post_withdrawal_keep_data", Boolean),
        Column("brc_opt_out", Boolean),
        Column("ecrf_timestamp", BigInteger, index=True, nullable=False),

        Column("last_updated_datetime", DateTime, nullable=False),
        Column("last_updated_by_user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
        UniqueConstraint(
            'project_id',
            'ecrf_participant_identifier',
            name='uix__ecrf_details__project_id__ecrf_participant_identifier',
        )
     )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("ecrf_detail", meta, autoload=True)
    t.drop()
