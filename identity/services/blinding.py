from flask_login import current_user
from lbrc_flask.database import db
from sqlalchemy import select
from identity.model.blinding import Blinding
from identity.model.id import PseudoRandomId


def get_study_blinding_ids(study, unblind_id):
    blinding_types = [t for t in study.blinding_types if not t.deleted]
    
    existing_blindings = db.session.execute(
        select(Blinding)
        .where(Blinding.blinding_type_id.in_([bt.id for bt in blinding_types]))
        .where(Blinding.unblind_id == unblind_id)
    ).scalars().all()

    missing_blinding_type = [
        (bt, bt.pseudo_random_id_provider.allocate_id())
        for bt in blinding_types if bt.id not in [b.blinding_type_id for b in existing_blindings]
    ]

    new_blindings = [
        Blinding(
            unblind_id=unblind_id,
            blinding_type=bt,
            pseudo_random_id=id,
            last_updated_by_user=current_user,
        )
        for bt, id in missing_blinding_type
    ]

    return existing_blindings + new_blindings


def get_blinding_type_id(blinding_type, unblind_id):
    blinding = db.session.execute(
        select(Blinding)
        .where(Blinding.blinding_type_id == blinding_type.id)
        .where(Blinding.unblind_id == unblind_id)
    ).scalar_one_or_none()

    if not blinding:
        pseudo_random_id = blinding_type.pseudo_random_id_provider.allocate_id()

        blinding = Blinding(
            unblind_id=unblind_id,
            blinding_type=blinding_type,
            pseudo_random_id=pseudo_random_id,
            last_updated_by_user=current_user,
        )
    
    return blinding
