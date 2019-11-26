from sqlalchemy import (
    MetaData,
    Table,
    Column,
    DateTime,
    Index
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    dr = Table("demographics_request", meta, autoload=True)

    lookup_completed_datetime = Column("lookup_completed_datetime", DateTime)
    lookup_completed_datetime.create(dr)
    result_created_datetime = Column("result_created_datetime", DateTime)
    result_created_datetime.create(dr)
    result_downloaded_datetime = Column("result_downloaded_datetime", DateTime)
    result_downloaded_datetime.create(dr)
    data_extracted_datetime = Column("data_extracted_datetime", DateTime)
    data_extracted_datetime.create(dr)
    paused_datetime = Column("paused_datetime", DateTime)
    paused_datetime.create(dr)

    idx = Index('idx_demographics_request_lookup_completed_datetime', dr.c.lookup_completed_datetime)
    idx.create(migrate_engine)
    idx = Index('idx_demographics_request_result_created_datetime', dr.c.result_created_datetime)
    idx.create(migrate_engine)
    idx = Index('idx_demographics_request_result_downloaded_datetime', dr.c.result_downloaded_datetime)
    idx.create(migrate_engine)
    idx = Index('idx_demographics_request_data_extracted_datetime', dr.c.data_extracted_datetime)
    idx.create(migrate_engine)

def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("demographics_request", meta, autoload=True)
    t.c.lookup_completed_datetime.drop()
    t.c.result_created_datetime.drop()
    t.c.result_downloaded_datetime.drop()
    t.c.data_extracted_datetime.drop()
    t.c.paused_datetime.drop()
