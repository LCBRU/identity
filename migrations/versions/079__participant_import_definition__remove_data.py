def upgrade(migrate_engine):
    migrate_engine.execute("""
        DELETE FROM participant_import_definition;
    """)


def downgrade(migrate_engine):
    pass