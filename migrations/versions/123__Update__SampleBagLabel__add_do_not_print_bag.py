from sqlalchemy import (
    Boolean,
    MetaData,
    Table,
    Column,
)


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    t = Table("sample_bag_label", meta, autoload=True)

    do_not_print_bag = Column("do_not_print_bag", Boolean, default=False)
    do_not_print_bag.create(t)
    t.c.do_not_print_bag.alter(nullable=False)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    idp = Table("sample_bag_label", meta, autoload=True)
    idp.c.do_not_print_bag.drop()
