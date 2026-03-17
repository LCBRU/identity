from lbrc_flask.database import db


class Study(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    edge_id = db.Column(db.Integer, nullable=True)
    civicrm_study_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(50), nullable=False)

    def __str__(self):
        return self.name or ""
