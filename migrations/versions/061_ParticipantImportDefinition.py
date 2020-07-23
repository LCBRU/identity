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
    t = Table(
        "participant_import_definition",
        meta,
        Column("id", Integer, primary_key=True),

        Column("name", NVARCHAR(200), nullable=False),

        Column("recruitment_date_column_name", NVARCHAR(100)),
        Column("first_name_column_name", NVARCHAR(100)),
        Column("last_name_column_name", NVARCHAR(100)),
        Column("postcode_column_name", NVARCHAR(100)),
        Column("birth_date_column_name", NVARCHAR(100)),
        Column("non_completion_reason_column_name", NVARCHAR(100)),
        Column("withdrawal_date_column_name", NVARCHAR(100)),

        Column("withdrawn_from_study_column_name", NVARCHAR(100)),
        Column("withdrawn_from_study_values", NVARCHAR(500)),

        Column("sex_column_name", NVARCHAR(100)),
        Column("sex_column_map", NVARCHAR(500)),

        Column("complete_or_expected_column_name", NVARCHAR(100)),
        Column("complete_or_expected_values", NVARCHAR(500)),

        Column("post_withdrawal_keep_samples_column_name", NVARCHAR(100)),
        Column("post_withdrawal_keep_samples_values", NVARCHAR(500)),

        Column("post_withdrawal_keep_data_column_name", NVARCHAR(100)),
        Column("post_withdrawal_keep_data_values", NVARCHAR(500)),

        Column("brc_opt_out_column_name", NVARCHAR(100)),
        Column("brc_opt_out_values", NVARCHAR(500)),

        Column("excluded_from_analysis_column_name", NVARCHAR(100)),
        Column("excluded_from_analysis_values", NVARCHAR(500)),

        Column("excluded_from_study_column_name", NVARCHAR(100)),
        Column("excluded_from_study_values", NVARCHAR(500)),

        Column("identities_map", NVARCHAR(500)),

        Column("last_updated_datetime", DateTime, nullable=False),
        Column("last_updated_by_user_id", Integer, ForeignKey(u.c.id), index=True, nullable=False),
     )
    t.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("participant_import_definition", meta, autoload=True)
    t.drop()
