def upgrade(migrate_engine):
    migrate_engine.execute("""
        DELETE FROM participant_identifiers__participant_identifier_sources;
    """)
    migrate_engine.execute("""
        DELETE FROM ecrf_participant_identifier_source;
    """)
    migrate_engine.execute("""
        DELETE FROM participant_identifier_source;
    """)
    migrate_engine.execute("""
        DELETE FROM participant_identifier;
    """)
    migrate_engine.execute("""
        DELETE FROM ecrf_detail;
    """)


def downgrade(migrate_engine):
    pass