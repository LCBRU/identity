import datetime
import re
from flask_admin.contrib.sqla import fields
from flask_login import current_user
from lbrc_flask.database import db
from identity.model.security import User
from lbrc_flask.security import Role
from wtforms.validators import ValidationError
from identity.model import Study
from identity.api.model import ApiKey
from identity.ecrfs.model import (
    RedcapInstance,
    RedcapProject,
    ParticipantImportDefinition,
)
from flask_admin.form import rules
from lbrc_flask.admin import AdminCustomView, init_admin as flask_init_admin


class QuerySelectMultipleFieldSet(fields.QuerySelectMultipleField):
    def populate_obj(self, obj, name):
        setattr(obj, name, set(self.data))


class UserView(AdminCustomView):
    form_columns = ["username", "first_name", "last_name", "studies", "active", "roles"]

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


class StudyView(AdminCustomView):
    can_delete = False
    can_edit = False
    form_columns = ["name"]


class RedcapInstanceView(AdminCustomView):
    form_columns = ["name", "database_name", "base_url"]

    def on_model_change(self, form, model, is_created):
        model.last_updated_datetime = datetime.datetime.utcnow()
        model.last_updated_by_user = current_user


class RedcapProjectView(AdminCustomView):
    form_columns = ["redcap_instance", "project_id"]

    def on_model_change(self, form, model, is_created):
        model.last_updated_datetime = datetime.datetime.utcnow()
        model.last_updated_by_user = current_user


class ParticipantImportDefinitionView(AdminCustomView):
    def valid_list_of_values(form, field):
        if field.data is None:
            return

        values = [i.strip() for i in field.data.split(',')]

        if any(len(i) == 0 for i in values):
            raise ValidationError('contains empty list item')

    def valid_map(form, field):
        if field.data is None:
            return

        regex = re.compile("^([^:,]+:[^:,]+(,|$))*$")
        print(field.data)
        if not regex.match(field.data):
            raise ValidationError('invalid key-value pairs')


    form_columns = [
        "recruitment_date_column_name",
        "first_name_column_name",
        "last_name_column_name",
        "postcode_column_name",
        "birth_date_column_name",
        "withdrawal_date_column_name",
        "withdrawn_from_study_column_name",
        "withdrawn_from_study_values",
        "sex_column_name",
        "sex_column_map",
        "complete_or_expected_column_name",
        "complete_or_expected_values",
        "post_withdrawal_keep_samples_column_name",
        "post_withdrawal_keep_samples_values",
        "post_withdrawal_keep_data_column_name",
        "post_withdrawal_keep_data_values",
        "brc_opt_out_column_name",
        "brc_opt_out_values",
        "excluded_from_analysis_column_name",
        "excluded_from_analysis_values",
        "excluded_from_study_column_name",
        "excluded_from_study_values",
        "identities_map",
    ]

    form_rules = [
        'csrf_token',
        "recruitment_date_column_name",
        "first_name_column_name",
        "last_name_column_name",
        "postcode_column_name",
        "birth_date_column_name",
        "withdrawal_date_column_name",
        rules.Header("Withdrawn from Study"),
        "withdrawn_from_study_column_name",
        "withdrawn_from_study_values",
        rules.Header("Sex"),
        "sex_column_name",
        "sex_column_map",
        rules.Header("Complete or Expected to Complete Study"),
        "complete_or_expected_column_name",
        "complete_or_expected_values",
        rules.Header("Post Withdrawal Keep Samples?"),
        "post_withdrawal_keep_samples_column_name",
        "post_withdrawal_keep_samples_values",
        rules.Header("Post Withdrawal Keep Data?"),
        "post_withdrawal_keep_data_column_name",
        "post_withdrawal_keep_data_values",
        rules.Header("Opt Out of BRC"),
        "brc_opt_out_column_name",
        "brc_opt_out_values",
        rules.Header("Excluded from Analysis"),
        "excluded_from_analysis_column_name",
        "excluded_from_analysis_values",
        rules.Header("Excluded from Study"),
        "excluded_from_study_column_name",
        "excluded_from_study_values",
        "identities_map",
    ]

    list_desc = 'Comma separated list of values'
    map_desc = 'Comma separated list of key-value pairs, separated by a colon'

    column_descriptions = dict(
        withdrawn_from_study_values=list_desc,
        complete_or_expected_values=list_desc,
        post_withdrawal_keep_samples_values=list_desc,
        post_withdrawal_keep_data_values=list_desc,
        brc_opt_out_values=list_desc,
        excluded_from_analysis_values=list_desc,
        excluded_from_study_values=list_desc,
        identities_map=map_desc,
        sex_column_map=map_desc,
    )

    form_args = dict(
        withdrawn_from_study_column_name=dict(label='Column Name'),
        withdrawn_from_study_values=dict(label='Values', validators=[valid_list_of_values]),
        sex_column_name=dict(label='Column Name'),
        sex_column_map=dict(label='Value Maps', validators=[valid_map]),
        complete_or_expected_column_name=dict(label='Column Name'),
        complete_or_expected_values=dict(label='Values', validators=[valid_list_of_values]),
        post_withdrawal_keep_samples_column_name=dict(label='Column Name'),
        post_withdrawal_keep_samples_values=dict(label='Values', validators=[valid_list_of_values]),
        post_withdrawal_keep_data_column_name=dict(label='Column Name'),
        post_withdrawal_keep_data_values=dict(label='Values', validators=[valid_list_of_values]),
        brc_opt_out_column_name=dict(label='Column Name'),
        brc_opt_out_values=dict(label='Values', validators=[valid_list_of_values]),
        excluded_from_analysis_column_name=dict(label='Column Name'),
        excluded_from_analysis_values=dict(label='Values', validators=[valid_list_of_values]),
        excluded_from_study_column_name=dict(label='Column Name'),
        excluded_from_study_values=dict(label='Values', validators=[valid_list_of_values]),
        identities_map=dict(validators=[valid_map]),
    )

    def on_model_change(self, form, model, is_created):
        model.last_updated_datetime = datetime.datetime.utcnow()
        model.last_updated_by_user = current_user


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
            StudyView(Study, db.session),
            UserView(User, db.session),
            ApiKeyView(ApiKey, db.session),
            RedcapInstanceView(RedcapInstance, db.session),
            RedcapProjectView(RedcapProject, db.session),
            ParticipantImportDefinitionView(ParticipantImportDefinition, db.session),
        ]
    )
