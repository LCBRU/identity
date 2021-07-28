from sqlalchemy import (
    MetaData,
    Table,
    Column,
    NVARCHAR,
)


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    t = Table("demographics_request_column_definition", meta, autoload=True)

    gender_female_value = Column("gender_female_value", NVARCHAR(10))
    gender_female_value.create(t)

    gender_male_value = Column("gender_male_value", NVARCHAR(10))
    gender_male_value.create(t)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    t = Table("demographics_request_column_definition", meta, autoload=True)

    t.c.gender_female_value.drop()
    t.c.gender_male_value.drop()

