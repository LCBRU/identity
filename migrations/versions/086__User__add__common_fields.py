from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Boolean,
)

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("user", meta, autoload=True)

    ldap_user = Column("ldap_user", Boolean)
    ldap_user.create(t)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("user", meta, autoload=True)

    t.c.ldap_user.drop()
