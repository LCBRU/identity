from sqlalchemy import (
    MetaData,
    Table,
)
from lbrc_flask.security.migrations import add_audit_mixin_columns, delete_audit_mixin_columns


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    for type in ['bioresource_id', 'legacy_id', 'pseudo_random_id']:
        t = Table(type, meta, autoload=True)

        add_audit_mixin_columns(t)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    for type in ['bioresource_id', 'legacy_id', 'pseudo_random_id']:
        t = Table(type, meta, autoload=True)

        delete_audit_mixin_columns(t)
