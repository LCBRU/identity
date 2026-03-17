from lbrc_flask.database import db
from sqlalchemy import func
from identity.model import Study
from identity.model.id import (
    PseudoRandomIdProvider,
    PseudoRandomId,
)
from identity.model.security import User


class BlindingType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    pseudo_random_id_provider_id = db.Column(db.Integer, db.ForeignKey(PseudoRandomIdProvider.id), nullable=False)
    pseudo_random_id_provider = db.relationship(PseudoRandomIdProvider)
    deleted = db.Column(db.Boolean, nullable=False, default=False)
    duplicate_number = db.Column(db.Integer, default=0, nullable=False)
    study_id = db.Column(db.Integer, db.ForeignKey(Study.id), nullable=False)
    study = db.relationship(Study, backref=db.backref("blinding_types"))

    def __repr__(self):
        return self.name

    def __lt__(self, other):
        return self.name < other.name


class Blinding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unblind_id = db.Column(db.String(100), nullable=False)
    blinding_type_id = db.Column(db.Integer, db.ForeignKey(BlindingType.id), nullable=False)
    blinding_type = db.relationship(BlindingType, backref=db.backref("blindings"))
    pseudo_random_id_id = db.Column(db.Integer, db.ForeignKey(PseudoRandomId.id), nullable=False)
    pseudo_random_id = db.relationship(PseudoRandomId)
    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=func.now())
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    def __repr__(self):
        return '; '.join([
            self.blinding_type.name,
            self.unblind_id,
            self.pseudo_random_id.full_code,
        ])

    def __lt__(self, other):
        return self.name < other.name
