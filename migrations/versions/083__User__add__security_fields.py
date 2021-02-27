from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    DateTime,
    NVARCHAR,
)
from migrate.changeset.constraint import UniqueConstraint

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("user", meta, autoload=True)

    t.c.created_datetime.alter(name='date_created')

    email = Column("email", NVARCHAR(255), unique=True)
    email.create(t, unique_name='udx__user__email')

    password = Column("password", NVARCHAR(255))
    password.create(t)

    confirmed_at = Column("confirmed_at", DateTime())
    confirmed_at.create(t)

    last_login_at = Column("last_login_at", DateTime())
    last_login_at.create(t)

    current_login_at = Column("current_login_at", DateTime())
    current_login_at.create(t)

    last_login_ip = Column("last_login_ip", NVARCHAR(50))
    last_login_ip.create(t)

    current_login_ip = Column("current_login_ip", NVARCHAR(50))
    current_login_ip.create(t)

    login_count = Column("login_count", Integer)
    login_count.create(t)


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("user", meta, autoload=True)

    t.c.date_created.alter(name='created_datetime')

    email_cons = UniqueConstraint(t.c.email, name='udx__user__email')
    email_cons.drop()

    t.c.email.drop()
    t.c.password.drop()
    t.c.confirmed_at.drop()
    t.c.last_login_at.drop()
    t.c.current_login_at.drop()
    t.c.last_login_ip.drop()
    t.c.current_login_ip.drop()
    t.c.login_count.drop()
