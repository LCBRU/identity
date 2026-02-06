import uuid
from lbrc_flask.database import db, GUID
from identity.model.security import User
from sqlalchemy import select


def get_api_key(request):
    if not request.args.get('api_key'):
        return None

    api_key = request.args.get('api_key')

    return db.session.execute(select(ApiKey).where(ApiKey.key ==uuid.UUID(api_key))).scalar_one_or_none()


class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(GUID, nullable=False, default=uuid.uuid4)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User, backref=db.backref("api_key", uselist=False))

    def __repr__(self):
        return f'API Key for User {self.user.full_name}'
