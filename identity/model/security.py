import ldap
from datetime import datetime
from flask import current_app
from flask_login import UserMixin
from identity.database import db
from identity.utils import log_exception


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


roles_users = db.Table(
    'roles_users',
    db.Column(
        'user_id',
        db.Integer(),
        db.ForeignKey('user.id'),
    ),
    db.Column(
        'role_id',
        db.Integer(),
        db.ForeignKey('role.id'),
    ),
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    active = db.Column(db.Boolean, default=True)
    created_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    studies = db.relationship(
        "Study", secondary=users_studies, collection_class=set, backref=db.backref("users", lazy="joined")
    )
    roles = db.relationship(
        "Role", secondary=roles_users, collection_class=set, backref=db.backref("users", lazy="joined")
    )

    @property
    def is_active(self):
        return self.active

    @property
    def is_admin(self):
        return Role.ADMIN_ROLENAME in [r.name for r in self.roles]

    @property
    def full_name(self):
        user = self._search_ldap()

        return f"{user['given_name']} {user['surname']}".strip()

    @property
    def email(self):
        user = self._search_ldap()
        return user['email']

    def __str__(self):
        return self.email or self.username

    def _search_ldap(self):
        if current_app.config['TESTING']:
            return {
                'username': self.username,
                'email': '',
                'name': '',
                'surname': '',
                'given_name': '',
            }

        l = ldap.initialize(current_app.config['LDAP_URI'])
        l.protocol_version = 3
        l.set_option(ldap.OPT_REFERRALS, 0)

        try:
            l.simple_bind_s(
                current_app.config['LDAP_USER'],
                current_app.config['LDAP_PASSWORD'],
            )

            search_result = l.search_s(
                'DC=xuhl-tr,DC=nhs,DC=uk',
                ldap.SCOPE_SUBTREE,
                'sAMAccountName={}'.format(self.username),
            )

        except ldap.LDAPError as e:
            log_exception(e)

        if isinstance(search_result[0][1], dict):
            user = search_result[0][1]
            return {
                'username': user['sAMAccountName'][0].decode("utf-8"),
                'email': user['mail'][0].decode("utf-8"),
                'name': user['name'][0].decode("utf-8"),
                'surname': user['sn'][0].decode("utf-8"),
                'given_name': user['givenName'][0].decode("utf-8"),
            }
        else:
            return {
                'username': self.username,
                'email': '',
                'name': '',
                'surname': self.last_name,
                'given_name': self.first_name,
            }

    def validate_password(self, password):
        if current_app.config['TESTING']:
            return True

        l = ldap.initialize(current_app.config['LDAP_URI'])
        l.protocol_version = 3
        l.set_option(ldap.OPT_REFERRALS, 0)

        try:
            l.simple_bind_s(self.email, password)
            return True

        except ldap.LDAPError as e:
            print(e)
            return False


class Role(db.Model):
    ADMIN_ROLENAME = 'admin'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    def __str__(self):
        return self.name or ""
