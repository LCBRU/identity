from datetime import datetime
from wtforms import (
    IntegerField,
    StringField,
    HiddenField,
    SelectField,
    BooleanField,
    SelectMultipleField,
)
from wtforms.validators import Length, DataRequired
from flask_wtf.file import FileRequired
from lbrc_flask.forms import SearchForm, FlashingForm, FileField
from identity.model.edge import EdgeSiteStudy


class ConfirmForm(FlashingForm):
    id = HiddenField("id", validators=[DataRequired()])


class DemographicsDefineColumnsForm(FlashingForm):
    uhl_system_number_column_id = SelectField('UHL System Number', coerce=int)
    nhs_number_column_id = SelectField('NHS Number', coerce=int)
    family_name_column_id = SelectField('Family Name', coerce=int)
    given_name_column_id = SelectField('Given Name', coerce=int)
    gender_column_id = SelectField('Gender', coerce=int)
    gender_female_value = StringField("Female Value (default 'f' or 'female')", validators=[Length(max=10)])
    gender_male_value = StringField("Male Value (default 'm' or 'male')", validators=[Length(max=10)])
    dob_column_id = SelectField('Date of Birth', coerce=int)
    postcode_column_id = SelectField('Postcode', coerce=int)

    def validate(self, extra_validators=None):
        rv = FlashingForm.validate(self, extra_validators)
        if not rv:
            return False

        gender_female_value = (self.gender_female_value.data or '').strip().lower()
        gender_male_value = (self.gender_male_value.data or '').strip().lower()

        if len(gender_female_value) == 0 or len(gender_male_value) == 0:
            return True

        if gender_female_value == gender_male_value:
            self.gender_male_value.errors.append('Female and Male values cannot be the same.')
            return False

        return True


def _get_clinical_area_choices():
    ess = EdgeSiteStudy.query.with_entities(EdgeSiteStudy.primary_clinical_management_areas.distinct()).all()
    return [(s[0], s[0]) for s in ess]


def _get_status_choices():
    ess = EdgeSiteStudy.query.with_entities(EdgeSiteStudy.project_site_status.distinct()).all()
    return [(s[0], s[0]) for s in ess]


def _get_principal_investigator_choices():
    ess = EdgeSiteStudy.query.with_entities(EdgeSiteStudy.principal_investigator.distinct()).all()
    return [('', '')] + [(s, s) for s in sorted(filter(None, [s[0] for s in ess]))]


def _get_lead_nurse_choices():
    ess = EdgeSiteStudy.query.with_entities(EdgeSiteStudy.project_site_lead_nurses.distinct()).all()
    return [('', '')] + [(s, s) for s in sorted(filter(None, [s[0] for s in ess]))]


def _get_rag_rating_choices():
    ess = EdgeSiteStudy.query.with_entities(EdgeSiteStudy.rag_rating.distinct()).all()
    return [('', '')] + [(s, s.title()) for s in sorted(filter(None, [s[0] for s in ess]))]


class TrackerSearchForm(SearchForm):
    clinical_area = SelectMultipleField('Clinical Area', choices=[])
    status = SelectMultipleField('Status', choices=[], default=['Open'])
    principal_investigator = SelectField('Principal Investigator', choices=[])
    lead_nurse = SelectField('Lead Nurse', choices=[])
    rag_rating = SelectField('RAG Rating', choices=[])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.clinical_area.choices = _get_clinical_area_choices()
        self.status.choices = _get_status_choices()
        self.principal_investigator.choices = _get_principal_investigator_choices()
        self.lead_nurse.choices = _get_lead_nurse_choices()
        self.rag_rating.choices = _get_rag_rating_choices()


class TrackerSearchGanttForm(TrackerSearchForm):
    start_year = SelectField('Start Date', choices=[], default=datetime.now().year)
    period = SelectField('Period', choices=[(1, '1 year'), (2, '2 years'), (3, '3 years'), (4, '4 years'), (5, '5 years')], default=1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        this_year = datetime.now().year
        self.start_year.choices = [(y, y) for y in range(this_year - 10, this_year + 10)]
