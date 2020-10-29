def upgrade(migrate_engine):
    migrate_engine.execute("""
        DELETE FROM ecrf_detail;
    """)


def downgrade(migrate_engine):
    pass