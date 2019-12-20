from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Text,
    DateTime,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("demographics_request", meta, autoload=True)

    pmi_data_pre_completed_datetime = Column("pmi_data_pre_completed_datetime", DateTime)
    pmi_data_pre_completed_datetime.create(t)
    pmi_data_post_completed_datetime = Column("pmi_data_post_completed_datetime", DateTime)
    pmi_data_post_completed_datetime.create(t)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("demographics_request", meta, autoload=True)
    t.c.pmi_data_pre_completed_datetime.drop()
    t.c.pmi_data_post_completed_datetime.drop()
