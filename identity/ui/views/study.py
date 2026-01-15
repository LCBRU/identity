from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
)
from markupsafe import Markup
from flask_login import current_user
from sqlalchemy import select

from identity.model.civicrm import CiviCrmStudy
from identity.services.civicrm import get_civicrm_study_choices, ParticipantSearchForm, get_civicrm_study_status_choices, get_participant_query
from .. import blueprint, db
from identity.model.blinding import Blinding
from identity.model import Study
from identity.model.id import PseudoRandomId
from ..decorators import assert_study_user
from identity.model.edge import EdgeSiteStudy
from lbrc_flask.forms import FlashingForm
from lbrc_flask.response import refresh_response
from wtforms import HiddenField, SelectField, StringField, IntegerField
from wtforms.validators import Length, DataRequired, Optional
from identity.model.civicrm import CiviCrmParticipant


class BlindingForm(FlashingForm):
    id = StringField("ID", validators=[DataRequired(), Length(max=100)], render_kw={"placeholder": "Participant ID"})


class UnblindingForm(FlashingForm):
    id = StringField("ID", validators=[DataRequired(), Length(max=100)], render_kw={"placeholder": "Blinded ID"})


class EditStudyForm(FlashingForm):
    id = HiddenField('id')
    name = StringField('Name', validators=[Length(max=50)])
    edge_id = IntegerField('EDGE ID', validators=[Optional()])
    civicrm_study_id = SelectField('CiviCRM Study', choices=[])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.civicrm_study_id.choices = [('', '')] + get_civicrm_study_choices()


class EditParticipantForm(FlashingForm):
    id = HiddenField('id')
    status_id = SelectField('Status', choices=[])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.status_id.choices = [('', '')] + get_civicrm_study_status_choices()


@blueprint.route("/study/<int:id>/blinding/", methods=['POST'])
@assert_study_user()
def blinding(id):
    study = db.get_or_404(Study, id)

    blinding_form = BlindingForm()

    if blinding_form.validate_on_submit():
        ids = study.get_blind_ids(blinding_form.id.data, current_user)

        db.session.add_all(ids)
        db.session.commit()

        flash(
            Markup(
                f'<span>Blind IDs created for ID \'{blinding_form.id.data}\'</span>'
                '<dl>' +
                ''.join([f'<dt>{id.blinding_type.name}</dt><dd>{id.pseudo_random_id.full_code}</dd>' for id in ids]) +
                '</dl>'
            ),'success')

    return redirect(url_for("ui.study", id=study.id))


@blueprint.route("/study/<int:id>/unblinding/", methods=['POST'])
@assert_study_user()
def unblinding(id):
    study = db.get_or_404(Study, id)

    un_blinding_form = UnblindingForm()

    if un_blinding_form.validate_on_submit():
        blinding = Blinding.query.join(PseudoRandomId).filter_by(full_code=un_blinding_form.id.data).first()

        if blinding is None or blinding.blinding_type.study != study:
            flash(
                'Blind ID "{}" not found for study {}'.format(
                    un_blinding_form.id.data,
                    study.name,
                ),
                'warning',
            )
        else:
            flash(
                '{} ID "{}" is unblinded to "{}"'.format(
                    blinding.blinding_type.name,
                    blinding.pseudo_random_id.full_code,
                    blinding.unblind_id,
                ),
                'success',
            )

    return redirect(url_for("ui.study", id=study.id))


@blueprint.route("/study/<int:id>")
@assert_study_user()
def study(id):
    study = db.get_or_404(Study, id)
    blinding_form = None
    unblinding_form = None
    search_form = ParticipantSearchForm(formdata=request.args, search_placeholder='Search name or identifiers')

    if study.edge_id:
        q = select(EdgeSiteStudy).where(EdgeSiteStudy.project_id == study.edge_id)
        edge_site_study = db.session.execute(q).scalar_one_or_none()
    else:
        edge_site_study = None

    if study.civicrm_study_id:
        q = select(CiviCrmStudy).where(CiviCrmStudy.id == study.civicrm_study_id)
        civicrm_study = db.session.execute(q).scalar_one_or_none()
    else:
        civicrm_study = None

    if study.blinding_types:
        blinding_form = BlindingForm()
        unblinding_form = UnblindingForm()

    q = get_participant_query(search_form, study.civicrm_study_id).order_by(CiviCrmParticipant.subject)

    participants = db.paginate(
        select=q,
        page=search_form.page.data,
        per_page=10,
        error_out=False,
    )

    return render_template(
        "ui/study/index.html",
        study=study,
        blinding_form=blinding_form,
        unblinding_form=unblinding_form,
        edge_site_study=edge_site_study,
        civicrm_study=civicrm_study,
        search_form=search_form,
        participants=participants,
    )


@blueprint.route("/study/<int:id>/edit", methods=['GET', 'POST'])
@assert_study_user()
def study_edit(id):
    study = db.get_or_404(Study, id)

    form = EditStudyForm(obj=study)

    if form.validate_on_submit():
        study.edge_id = form.edge_id.data
        study.name = form.name.data
        study.civicrm_study_id = form.civicrm_study_id.data
        db.session.add(study)
        db.session.commit()
        return refresh_response()

    return render_template(
        "lbrc/form_modal.html",
        title=f"Edit Study {study.name}",
        form=form,
        url=url_for('ui.study_edit', id=id),
    )


@blueprint.route("/study/<int:id>/partcipant/<int:participant_id>/edit", methods=['GET', 'POST'])
@assert_study_user()
def participant_edit(id, participant_id):
    study = db.get_or_404(Study, id)
    participant = db.get_or_404(CiviCrmParticipant, participant_id)

    form = EditParticipantForm(obj=participant)

    if form.validate_on_submit():
        participant.status_id = form.status_id.data
        db.session.add(participant)
        db.session.commit()
        return refresh_response()

    return render_template(
        "lbrc/form_modal.html",
        title=f"Edit Participant {participant.contact.full_name}",
        form=form,
        url=url_for('ui.participant_edit', id=id, participant_id=participant_id),
    )
