from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    NVARCHAR,
    BOOLEAN,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    dr = Table("demographics_request", meta, autoload=True)

    submitted_datetime = Column("submitted_datetime", DateTime, index=True)
    submitted_datetime.create(dr, index_name='idx_demographics_request_submitted_datetime')

def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("demographics_request", meta, autoload=True)
    t.c.submitted_datetime.drop()
