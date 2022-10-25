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

    i = Table("id_provider", meta, autoload=True)
    t = Table("label_batch", meta, autoload=True)

    print_recruited_notice = Column("print_recruited_notice", Boolean)
    print_recruited_notice.create(t)

    aliquot_id_provider_id = Column("aliquot_id_provider_id", Integer, index=True)
    aliquot_id_provider_id.create(t, index_name=f'idx__label_batch__aliquot_id_provider_id')

    t.append_constraint(ForeignKeyConstraint([aliquot_id_provider_id], [i.c.id_provider_id]))


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    idp = Table("label_batch", meta, autoload=True)
    idp.c.print_recruited_notice.drop()
    idp.c.aliquot_id_provider_id.drop()
