from datetime import datetime
from lbrc_flask.database import db
from identity.model import Study
from identity.model.id import (
    PseudoRandomIdProvider,
    PseudoRandomId,
)
from identity.model.security import User


class BlindingSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    study_id = db.Column(db.Integer, db.ForeignKey(Study.id), nullable=False)
    study = db.relationship(Study, backref=db.backref("blinding_sets"))

    def __repr__(self):
        return self.name

    def __lt__(self, other):
        return self.name < other.name

    def get_blind_ids(self, unblind_id, user):
        result = []

        for bt in self.blinding_types:
            blind_id = bt.get_blind_id(unblind_id, user)
            if blind_id:
                result.append(blind_id)

        return result

    def get_unblind_id(self, blind_id):
        for bt in self.blinding_types:
            unblind_id = bt.get_unblind_id(blind_id)
            if unblind_id:
                return unblind_id


class BlindingType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    blinding_set_id = db.Column(db.Integer, db.ForeignKey(BlindingSet.id), nullable=False)
    blinding_set = db.relationship(BlindingSet, backref=db.backref("blinding_types"))
    pseudo_random_id_provider_id = db.Column(db.Integer, db.ForeignKey(PseudoRandomIdProvider.id), nullable=False)
    pseudo_random_id_provider = db.relationship(PseudoRandomIdProvider)
    deleted = db.Column(db.Boolean, nullable=False, default=False)
    duplicate_number = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        return self.name

    def __lt__(self, other):
        return self.name < other.name

    def get_blind_id(self, unblind_id, user):
        blinding = (
            Blinding.query
            .filter_by(blinding_type_id=self.id)
            .filter_by(unblind_id=unblind_id)
            .first()
        )
        if not blinding:
            pseudo_random_id = self.pseudo_random_id_provider.allocate_id(user)

            blinding = Blinding(
                unblind_id=unblind_id,
                blinding_type=self,
                pseudo_random_id=pseudo_random_id,
                last_updated_by_user=user,
            )
        
        return blinding

    def get_unblind_id(self, blind_id):
        blinding = (
            Blinding.query
            .filter_by(blinding_type_id=self.id)
            .join(PseudoRandomId)
            .filter_by(full_code=blind_id)
            .first()
        )
        
        return blinding


class Blinding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unblind_id = db.Column(db.String(100), nullable=False)
    blinding_type_id = db.Column(db.Integer, db.ForeignKey(BlindingType.id), nullable=False)
    blinding_type = db.relationship(BlindingType, backref=db.backref("blindings"))
    pseudo_random_id_id = db.Column(db.Integer, db.ForeignKey(PseudoRandomId.id), nullable=False)
    pseudo_random_id = db.relationship(PseudoRandomId)
    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
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
