from lbrc_flask.database import db


class Study(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    edge_id = db.Column(db.Integer, nullable=True)
    civicrm_study_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(50), nullable=False)

    def __str__(self):
        return self.name or ""

    def get_blind_ids(self, unblind_id, user):
        result = []

        for bt in [t for t in self.blinding_types if not t.deleted]:
            blind_id = bt.get_blind_id(unblind_id, user)
            if blind_id:
                result.append(blind_id)

        return result
