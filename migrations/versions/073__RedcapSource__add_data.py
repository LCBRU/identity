from sqlalchemy.schema import ForeignKeyConstraint


def upgrade(migrate_engine):
    migrate_engine.execute("""
        UPDATE rp
        SET ecrf_source_id = es.id
        FROM redcap_project rp
        JOIN ecrf_source es
            ON es.redcap_project_id = rp.id
    """)


def downgrade(migrate_engine):
    pass
