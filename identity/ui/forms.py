from flask import flash
from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    StringField,
    TextAreaField,
    HiddenField,
    SelectField,
    BooleanField,
)
from wtforms.validators import Length, DataRequired
from flask_wtf.file import FileField as _FileField, FileAllowed, FileRequired
from wtforms.widgets import FileInput as _FileInput


class FlashingForm(FlaskForm):
    def validate_on_submit(self):
        result = super(FlashingForm, self).validate_on_submit()

        if not result:
            for field, errors in self.errors.items():
                for error in errors:
                    flash(
                        "Error in the {} field - {}".format(
                            getattr(self, field).label.text, error
                        ),
                        "error",
                    )
        return result


class FileInput(_FileInput):

    def __call__(self, field, **kwargs):
        if field.accept:
            kwargs[u'accept'] = ','.join(field.accept)
        return _FileInput.__call__(self, field, **kwargs)


class FileField(_FileField):
    widget = FileInput()

    def __init__(self, *args, **kwargs):
        self.accept = kwargs.pop('accept', None)
        super(FileField, self).__init__(*args, **kwargs)


class SearchForm(FlashingForm):
    search = StringField("Search", validators=[Length(max=20)])
    page = IntegerField("Page", default=1)


class ConfirmForm(FlashingForm):
    id = HiddenField("id", validators=[DataRequired()])


class BlindingForm(FlashingForm):
    id = StringField("ID", validators=[DataRequired(), Length(max=100)])
    blinding_set_id = SelectField('Set', coerce=int)


class UnblindingForm(FlashingForm):
    id = StringField("ID", validators=[DataRequired(), Length(max=100)])


class DemographicsLookupForm(FlashingForm):
    upload = FileField(
        'Participant File',
        accept=[
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
            '.csv',
        ],
        validators=[FileRequired()]
    )

class DemographicsDefineColumnsForm(FlashingForm):
    uhl_system_number_column_id = SelectField('UHL System Number', coerce=int)
    nhs_number_column_id = SelectField('NHS Number', coerce=int)
    family_name_column_id = SelectField('Family Name', coerce=int)
    given_name_column_id = SelectField('Given Name', coerce=int)
    gender_column_id = SelectField('Gender', coerce=int)
    dob_column_id = SelectField('Date of Birth', coerce=int)
    postcode_column_id = SelectField('Postcode', coerce=int)


class DemographicsSearchForm(FlashingForm):
    search = StringField("Search", validators=[Length(max=20)])
    page = IntegerField("Page", default=1)
    show_downloaded = BooleanField('Downloaded')
    show_deleted = BooleanField('Deleted')


class DemographicsAdminSearchForm(DemographicsSearchForm):
    owner_user_id = SelectField('Owner', coerce=int, choices=[])


class LabelDefinition(FlashingForm):
    participant_id = StringField("Participant Identifier", validators=[DataRequired(), Length(max=100)])
