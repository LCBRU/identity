from lbrc_flask.database import db
from lbrc_flask.security import User as BaseUser


users_studies = db.Table(
    'users_studies',
    db.Column(
        'user_id',
        db.Integer(),
        db.ForeignKey('user.id'),
        primary_key=True,
    ),
    db.Column(
        'study_id',
        db.Integer(),
        db.ForeignKey('study.id'),
        primary_key=True,
    ),
)


class User(BaseUser):
    __table_args__ = {'extend_existing': True}

    studies = db.relationship(
        "Study", secondary=users_studies, collection_class=set, backref=db.backref("users", lazy="joined")
    )

