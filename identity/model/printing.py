from lbrc_flask.database import db


class LabelBatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


def _setup_alleviate():
    pass

def setup_packs():
    _setup_alleviate()

