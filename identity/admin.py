from flask_admin.contrib.sqla import fields
from lbrc_flask.database import db
from identity.model.blinding import BlindingType
from identity.model.id import BioresourceIdProvider, LegacyIdProvider, PseudoRandomIdProvider, SequentialIdProvider
from identity.model.security import User
from lbrc_flask.security import Role
from identity.model import Study
from identity.api.model import ApiKey
from lbrc_flask.admin import AdminCustomView, init_admin as flask_init_admin

from identity.printing.model import LabelPack


class QuerySelectMultipleFieldSet(fields.QuerySelectMultipleField):
    def populate_obj(self, obj, name):
        setattr(obj, name, list(set(self.data)))


class UserView(AdminCustomView):
    form_columns = ["username", "first_name", "last_name", "studies", "active", "roles"]
    column_list = ['username', 'first_name', 'last_name', 'active', 'last_login_at', 'ldap_user']
    # can_create = False

    # form_args and form_overrides required to allow studies and roles to be sets.
    form_args = {
        'studies': {
            'query_factory': lambda: db.session.query(Study)
        },
        'roles': {
            'query_factory': lambda: db.session.query(Role)
        },
    }
    form_overrides = {
        'studies': QuerySelectMultipleFieldSet,
        'roles': QuerySelectMultipleFieldSet,
    }
    column_searchable_list = [User.username, User.first_name, User.last_name, User.email]


class StudyView(AdminCustomView):
    form_columns = ["name", "edge_id"]
    column_searchable_list = [Study.name]


class ApiKeyView(AdminCustomView):
    form_columns = ["user"]

    form_args = {
        'user': {
            'query_factory': lambda: db.session.query(User),
        },
    }


class BlindingTypeView(AdminCustomView):
    column_list = form_columns = [
        "study",
        "pseudo_random_id_provider",
        "name",
        "deleted",
    ]


class PseudoRandomIdProviderView(AdminCustomView):
    can_delete = False
    column_list = form_columns = [
        "name",
        "prefix",
    ]


class BioresourceIdProviderView(AdminCustomView):
    can_delete = False
    column_list = form_columns = [
        "name",
        "prefix",
    ]


class LegacyIdProviderView(AdminCustomView):
    can_delete = False
    column_list = form_columns = [
        "name",
        "prefix",
        "number_fixed_length",
    ]


class SequentialIdProviderView(AdminCustomView):
    can_delete = False
    column_list = form_columns = [
        "name",
        "prefix",
        "zero_fill_size",
        "last_number",
    ]


class LabelPackView(AdminCustomView):
    pass

def init_admin(app, title):
    flask_init_admin(
        app,
        title,
        [
            ApiKeyView(ApiKey, db.session),
            StudyView(Study, db.session),
            UserView(User, db.session),
            BlindingTypeView(BlindingType, db.session),
            BioresourceIdProviderView(BioresourceIdProvider, db.session, category="ID Providers"),
            PseudoRandomIdProviderView(PseudoRandomIdProvider, db.session, category="ID Providers"),
            SequentialIdProviderView(SequentialIdProvider, db.session, category="ID Providers"),
            LegacyIdProviderView(LegacyIdProvider, db.session, category="ID Providers"),
            LabelPackView(LabelPack, db.session),
        ],
    )
