from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    ForeignKey,
    DateTime,
    NVARCHAR,
)
from sqlalchemy.schema import ForeignKeyConstraint

meta = MetaData()


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    pid = Table("participant_import_definition", meta, autoload=True)

    t = Table("ecrf_detail", meta, autoload=True)

    t.c.redcap_project_id.drop()

    participant_import_definition_id = Column("participant_import_definition_id", Integer, index=True)
    participant_import_definition_id.create(t, index_name='idx__ecrf_detail__participant_import_definition_id')

    t.append_constraint(ForeignKeyConstraint([participant_import_definition_id], [pid.c.id]))


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    t = Table("ecrf_detail", meta, autoload=True)

    t.c.participant_import_definition_id.drop()
