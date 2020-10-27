from sqlalchemy.schema import ForeignKeyConstraint


def upgrade(migrate_engine):
    migrate_engine.execute("""
    update redcap_project 
        set ecrf_source_id = (
            select es.id 
            from ecrf_source es 
            where es.redcap_project_id = redcap_project.id
        )
    );

    """)


def downgrade(migrate_engine):
    pass
