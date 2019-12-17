from sqlalchemy import (
    MetaData,
    Table,
    Column,
    NVARCHAR,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    t = Table("demographics_request_data", meta, autoload=True)

    uhl_s_number = Column("uhl_s_number", NVARCHAR(50))
    uhl_s_number.create(t)
    pmi_nhs_number = Column("pmi_nhs_number", NVARCHAR(50))
    pmi_nhs_number.create(t)
    pmi_uhl_s_number = Column("pmi_uhl_s_number", NVARCHAR(50))
    pmi_uhl_s_number.create(t)
    pmi_family_name = Column("pmi_family_name", NVARCHAR(50))
    pmi_family_name.create(t)
    pmi_given_name = Column("pmi_given_name", NVARCHAR(50))
    pmi_given_name.create(t)
    pmi_gender = Column("pmi_gender", NVARCHAR(50))
    pmi_gender.create(t)
    pmi_dob = Column("pmi_dob", NVARCHAR(50))
    pmi_dob.create(t)
    pmi_postcode = Column("pmi_postcode", NVARCHAR(50))
    pmi_postcode.create(t)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("demographics_request_data", meta, autoload=True)
    t.c.uhl_s_number.drop()
    t.c.pmi_nhs_number.drop()
    t.c.pmi_uhl_s_number.drop()
    t.c.pmi_family_name.drop()
    t.c.pmi_given_name.drop()
    t.c.pmi_gender.drop()
    t.c.pmi_dob.drop()
    t.c.pmi_postcode.drop()
