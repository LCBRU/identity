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

    drd = Table("demographics_request_data", meta, autoload=True)

    created_datetime = Column("created_datetime", DateTime)
    created_datetime.create(drd)
    processed_datetime = Column("processed_datetime", DateTime)
    processed_datetime.create(drd)

    idx = Index('idx_demographics_request_data_id_processed_datetime', drd.c.id, drd.c.processed_datetime)
    idx.create(migrate_engine)

def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("demographics_request_data", meta, autoload=True)
    t.c.created_datetime.drop()
    t.c.processed_datetime.drop()
