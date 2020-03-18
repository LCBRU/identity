from sqlalchemy import (
    MetaData,
    Table,
    Column,
    DateTime,
    Index,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("demographics_request_data", meta, autoload=True)

    pmi_pre_processed_datetime = Column("pmi_pre_processed_datetime", DateTime)
    pmi_pre_processed_datetime.create(t)
    pmi_post_processed_datetime = Column("pmi_post_processed_datetime", DateTime)
    pmi_post_processed_datetime.create(t)

    idx = Index(
        'idx_drd__pmi_pre_processed_datetime',
        t.c.request_id,
        t.c.pmi_pre_processed_datetime,
    )
    idx.create(migrate_engine)
    idx = Index(
        'idx_drd__pmi_post_processed_datetime',
        t.c.request_id,
        t.c.pmi_post_processed_datetime,
    )
    idx.create(migrate_engine)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("demographics_request_data", meta, autoload=True)
    t.c.pmi_pre_processed_datetime.drop()
    t.c.pmi_post_processed_datetime.drop()