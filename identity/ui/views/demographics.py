import os
from datetime import datetime
from functools import wraps
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort,
    send_file,
)
from markupsafe import Markup
from flask_login import current_user
from .. import blueprint, db
from lbrc_flask.forms import ConfirmForm, SearchForm, FlashingForm, FileField
from identity.demographics.model import (
    DemographicsRequest,
    DemographicsRequestXlsx,
    DemographicsRequestExcel97,
    DemographicsRequestCsv,
    DemographicsRequestColumn,
    DemographicsRequestColumnDefinition,
    User,
)
from identity.demographics import schedule_lookup_tasks
from identity.security import must_be_admin
from lbrc_flask.logging import log_exception
from flask_wtf.file import FileRequired
from wtforms import BooleanField, SelectField, StringField
from lbrc_flask.response import refresh_response
from wtforms.validators import Length


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
    skip_pmi = BooleanField('Skip PMI')


class DemographicsSearchForm(SearchForm):
    show_downloaded = BooleanField('Downloaded')
    show_deleted = BooleanField('Deleted')


class DemographicsAdminSearchForm(DemographicsSearchForm):
    owner_user_id = SelectField('Owner', coerce=int, choices=[])


def must_be_request_owner():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            dr = DemographicsRequest.query.get_or_404(request.view_args.get("id"))

            if current_user != dr.owner and not current_user.is_admin:
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


@blueprint.route("/demographics/")
def demographics():
    if current_user.is_admin:
        search_form = DemographicsAdminSearchForm(formdata=request.args, search_placeholder='Search Demographics Requests')

        submitter_ids = DemographicsRequest.query.with_entities(DemographicsRequest.owner_user_id.distinct()).filter(DemographicsRequest.owner_user_id != current_user.id).subquery()
        submitters = sorted(User.query.filter(User.id.in_(submitter_ids)).all(), key=lambda u: u.full_name)

        search_form.owner_user_id.choices = [(current_user.id, current_user.full_name)] + [(u.id, u.full_name) for u in submitters] + [(0, 'All')]
    else:
        search_form = DemographicsSearchForm(formdata=request.args)

    q = DemographicsRequest.query

    if search_form.search.data:
        q = q.filter(DemographicsRequest.filename.like('%{}%'.format(search_form.search.data)))

    if not search_form.show_deleted.data:
        q = q.filter(DemographicsRequest.deleted_datetime.is_(None))

    if not search_form.show_downloaded.data:
        q = q.filter(DemographicsRequest.result_downloaded_datetime.is_(None))

    if current_user.is_admin:
        owner_id = search_form.owner_user_id.data or current_user.id

        if owner_id > 0:
            q = q.filter(DemographicsRequest.owner_user_id == owner_id)
    else:
        q = q.filter(DemographicsRequest.owner == current_user)

    demographics_requests = q.order_by(DemographicsRequest.created_datetime.desc()).paginate(
        page=search_form.page.data, per_page=5, error_out=False
    )

    return render_template("ui/demographics/index.html", form=DemographicsLookupForm(), demographics_requests=demographics_requests, search_form=search_form)


@blueprint.route("/demographics/upload", methods=['POST'])
def demographics_upload():
    form = DemographicsLookupForm()

    if form.validate_on_submit():
        _, file_extension = os.path.splitext(form.upload.data.filename)

        if file_extension == '.csv':
            d = DemographicsRequestCsv(
                owner=current_user,
                last_updated_by_user=current_user,
                filename=form.upload.data.filename,
                skip_pmi=form.skip_pmi.data,
            )
        elif file_extension == '.xlsx':
            d = DemographicsRequestXlsx(
                owner=current_user,
                last_updated_by_user=current_user,
                filename=form.upload.data.filename,
                skip_pmi=form.skip_pmi.data,
            )
        elif file_extension == '.xls':
            d = DemographicsRequestExcel97(
                owner=current_user,
                last_updated_by_user=current_user,
                filename=form.upload.data.filename,
                skip_pmi=form.skip_pmi.data,
            )

        db.session.add(d)
        db.session.flush()

        os.makedirs(os.path.dirname(d.filepath), exist_ok=True)
        form.upload.data.save(d.filepath)

        try:
            for name in d.get_column_names():
                c = DemographicsRequestColumn(
                    demographics_request = d,
                    name=name,
                    last_updated_by_user=current_user,
                )
                db.session.add(c)
    
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            os.unlink(d.filepath)
            log_exception(e)
            flash('File contents are invalid', 'error')

            return redirect(url_for('ui.demographics'))

        return redirect(url_for('ui.demographics_define_columns', id=d.id))

    return redirect(url_for('ui.demographics'))


@blueprint.route("/demographics/define_columns/<int:id>", methods=['GET', 'POST'])
@must_be_request_owner()
def demographics_define_columns(id):
    dr = DemographicsRequest.query.get_or_404(id)

    if dr.deleted:
        flash('Cannot amend a request that is deleted.', 'error')
        return redirect(url_for('ui.demographics'))

    if dr.submitted:
        flash('Cannot amend a request that has been submitted.', 'error')
        return redirect(url_for('ui.demographics'))

    form = DemographicsDefineColumnsForm(obj=dr.column_definition)

    columns = sorted(dr.columns)

    for f in form:
        f.choices = [(0, '')] + [(c.id, c.name) for c in columns]

    if not form.uhl_system_number_column_id.data:
        form.uhl_system_number_column_id.data = dr.get_most_likely_uhl_system_number_column_id()
    if not form.nhs_number_column_id.data:
        form.nhs_number_column_id.data = dr.get_most_likely_nhs_number_column_id()
    if not form.family_name_column_id.data:
        form.family_name_column_id.data = dr.get_most_likely_family_name_column_id()
    if not form.given_name_column_id.data:
        form.given_name_column_id.data = dr.get_most_likely_given_name_column_id()
    if not form.gender_column_id.data:
        form.gender_column_id.data = dr.get_most_likely_gender_column_id()
    if not form.dob_column_id.data:
        form.dob_column_id.data = dr.get_most_likely_dob_column_id()
    if not form.postcode_column_id.data:
        form.postcode_column_id.data = dr.get_most_likely_postcode_column_id()

    if form.validate_on_submit():
        if dr.column_definition is None:
            dr.column_definition = DemographicsRequestColumnDefinition()

        dr.column_definition.last_updated_by_user = current_user

        dr.column_definition.uhl_system_number_column_id = form.uhl_system_number_column_id.data if form.uhl_system_number_column_id.data > 0 else None
        dr.column_definition.nhs_number_column_id = form.nhs_number_column_id.data if form.nhs_number_column_id.data > 0 else None
        dr.column_definition.family_name_column_id = form.family_name_column_id.data if form.family_name_column_id.data > 0 else None
        dr.column_definition.given_name_column_id = form.given_name_column_id.data if form.given_name_column_id.data > 0 else None
        dr.column_definition.gender_column_id = form.gender_column_id.data if form.gender_column_id.data > 0 else None
        dr.column_definition.dob_column_id = form.dob_column_id.data if form.dob_column_id.data > 0 else None
        dr.column_definition.postcode_column_id = form.postcode_column_id.data if form.postcode_column_id.data > 0 else None
        dr.column_definition.gender_female_value = form.gender_female_value.data
        dr.column_definition.gender_male_value = form.gender_male_value.data

        if not dr.column_definition.is_valid:
            flash(Markup('Column specification is invalid.  Please read the <a data-toggle="modal" data-target="#help_modal">help page <span class="fas fa-question-circle" ></span></a> for more details.'), 'error')
            db.session.rollback()
        else:
            db.session.add(dr)
            db.session.commit()

            return redirect(url_for('ui.demographics_submit', id=dr.id))

    return render_template(
        "lbrc/form_modal.html",
        title=f"Define Columns for {dr.filename}",
        form=form,
        url=url_for('ui.demographics_define_columns', id=id),
    )


@blueprint.route("/demographics/submit/<int:id>", methods=['GET', 'POST'])
@must_be_request_owner()
def demographics_submit(id):
    dr = DemographicsRequest.query.get_or_404(id)

    if dr.deleted:
        flash('Cannot submit a request that is deleted.', 'error')
        return refresh_response()

    if dr.submitted:
        flash('Cannot submit a request that has already been submitted.', 'error')
        return refresh_response()

    form = ConfirmForm(obj=dr)

    if form.validate_on_submit():
        dr.submitted_datetime = datetime.utcnow()

        db.session.add(dr)
        db.session.commit()

        schedule_lookup_tasks(dr.id)
        
        flash('Request submitted.')
        return refresh_response()

    return render_template("ui/demographics/submit.html", form=form, demographics_request=dr)


@blueprint.route("/demographics/resubmit/<int:id>")
@must_be_admin()
def demographics_resubmit(id):
    dr = DemographicsRequest.query.get_or_404(id)
    dr.paused_datetime = None

    db.session.add(dr)
    db.session.commit()

    schedule_lookup_tasks(id)
        
    flash('Request resubmitted.')
    return redirect(url_for('ui.demographics'))


@blueprint.route("/demographics/clear_error/<int:id>")
@must_be_admin()
def demographics_clear_error(id):
    dr = DemographicsRequest.query.get_or_404(id)
    dr.error_datetime = None
    dr.error_message = None

    db.session.add(dr)
    db.session.commit()

    schedule_lookup_tasks(id)
        
    flash('Error cleared and Request resubmitted.')
    return redirect(url_for('ui.demographics'))


@blueprint.route("/demographics/pause/<int:id>")
@must_be_admin()
def demographics_pause(id):

    dr = DemographicsRequest.query.get_or_404(id)

    if dr.deleted:
        flash('Request already deleted.', 'error')
    elif dr.result_created:
        flash('Request result already created.', 'error')
    else:
        dr.paused_datetime = datetime.utcnow()

        db.session.add(dr)
        db.session.commit()

        flash('Request paused.')

    return redirect(url_for('ui.demographics'))


@blueprint.route("/demographics/delete/<int:id>", methods=['POST'])
@must_be_request_owner()
def demographics_delete(id):
    dr = DemographicsRequest.query.get_or_404(id)

    if dr.deleted:
        return refresh_response()

    dr.deleted_datetime = datetime.utcnow()

    db.session.add(dr)
    db.session.commit()

    return refresh_response()


@blueprint.route("/demographics/download_result/<int:id>")
@must_be_request_owner()
def demographics_download_result(id):
    dr = DemographicsRequest.query.get_or_404(id)

    if not dr.result_created:
        abort(404)

    dr.result_downloaded_datetime = datetime.utcnow()
    db.session.add(dr)
    db.session.commit()

    return send_file(
        dr.result_filepath,
        as_attachment=True,
        download_name=dr.result_filename,
    )


@blueprint.route("/demographics/download_request/<int:id>")
@must_be_request_owner()
def demographics_download_request(id):
    dr = DemographicsRequest.query.get_or_404(id)

    dr.result_downloaded_datetime = datetime.utcnow()
    db.session.add(dr)
    db.session.commit()

    return send_file(
        dr.filepath,
        as_attachment=True,
        download_name=dr.filename,
    )


@blueprint.route("/demographics/column_help")
def demographics_column_help():
    return render_template("ui/demographics/column_help.html")
