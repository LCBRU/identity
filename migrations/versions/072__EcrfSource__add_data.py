from sqlalchemy.schema import ForeignKeyConstraint


def upgrade(migrate_engine):
    migrate_engine.execute("""
        INSERT INTO ecrf_source (redcap_project_id, type, name, last_updated_datetime, last_updated_by_user_id)
        SELECT
            id,
            'redcap_project',
            name,
            last_updated_datetime,
            last_updated_by_user_id
        FROM redcap_project;
        """)

    pass


def downgrade(migrate_engine):
    migrate_engine.execute("""
        DELETE FROM ecrf_source;
        """)
