from datetime import datetime
from identity.database import db
from identity.model.security import User


class Study(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __str__(self):
        return self.name or ""

    def get_blind_ids(self, unblind_id, user):
        result = []

        for bs in self.blinding_sets:
            for bt in [t for t in bs.blinding_types if not t.deleted]:
                blind_id = bt.get_blind_id(unblind_id, user)
                if blind_id:
                    result.append(blind_id)

        return result



class StudyParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    study_id = db.Column(db.Integer, db.ForeignKey(Study.id), nullable=False)
    study = db.relationship(Study, backref=db.backref("participants"))

    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)
