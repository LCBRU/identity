from sqlalchemy import (
    Boolean,
    ForeignKeyConstraint,
    Integer,
    MetaData,
    Table,
    Column,
)


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    t = Table("label_batch", meta, autoload=True)

    print_recruited_notice = Column("print_recruited_notice", Boolean)
    print_recruited_notice.create(t)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    idp = Table("label_batch", meta, autoload=True)
    idp.c.print_recruited_notice.drop()
