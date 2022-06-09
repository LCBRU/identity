import datetime
from flask_admin.contrib.sqla import fields
from flask_login import current_user
from lbrc_flask.database import db
from identity.model.security import User
from lbrc_flask.security import Role
from identity.model import Study
from identity.api.model import ApiKey
from identity.ecrfs.model import (
    EcrfSource,
    RedcapInstance,
    RedcapProject,
    ParticipantImportDefinition,
)
from lbrc_flask.admin import AdminCustomView, init_admin as flask_init_admin


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
    can_delete = False
    can_edit = False
    can_create = False
    form_columns = ["name"]
    column_searchable_list = [Study.name]


class RedcapInstanceView(AdminCustomView):
    can_delete = False
    can_edit = False
    can_create = False
    column_list = ['name', 'database_name', 'base_url', 'version']
    form_columns = ["name", "database_name", "base_url", 'version']

    def on_model_change(self, form, model, is_created):
        model.last_updated_datetime = datetime.datetime.utcnow()
        model.last_updated_by_user = current_user

class RedcapProjectView(AdminCustomView):
    can_delete = False
    can_edit = False
    can_create = False
    column_list = ["redcap_instance", "project_id", 'name']
    form_columns = ["redcap_instance", "project_id"]

    def on_model_change(self, form, model, is_created):
        model.last_updated_datetime = datetime.datetime.utcnow()
        model.last_updated_by_user = current_user


class ParticipantImportDefinitionView(AdminCustomView):
    can_delete = False
    can_edit = False
    can_create = False

    column_searchable_list = [Study.name, EcrfSource.name]
    column_list = ['study', 'ecrf_source', 'active']


class ApiKeyView(AdminCustomView):
    form_columns = ["user"]

    form_args = {
        'user': {
            'query_factory': lambda: db.session.query(User),
        },
    }


def init_admin(app, title):
    flask_init_admin(
        app,
        title,
        [
            ApiKeyView(ApiKey, db.session),
            StudyView(Study, db.session),
            UserView(User, db.session),
            RedcapInstanceView(RedcapInstance, db.session),
            RedcapProjectView(RedcapProject, db.session),
            ParticipantImportDefinitionView(ParticipantImportDefinition, db.session),
        ]
    )
