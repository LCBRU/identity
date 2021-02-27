from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    Markup,
)
from flask_login import current_user
from .. import blueprint, db
from identity.blinding.model import Blinding
from identity.model import Study, StudyParticipant
from identity.model.id import PseudoRandomId
from ..forms import BlindingForm, UnblindingForm
from ..decorators import assert_study_user


@blueprint.route("/study/<int:id>/blinding/", methods=['POST'])
@assert_study_user()
def blinding(id):
    study = Study.query.get_or_404(id)

    blinding_form = BlindingForm()

    if blinding_form.validate_on_submit():
        ids = study.get_blind_ids(blinding_form.id.data, current_user)

        db.session.add_all(ids)
        db.session.commit()

        flash(
            Markup(
                f'<strong>Blind IDs created for ID \'{blinding_form.id.data}\'</strong>'
                '<dl>' +
                ''.join([f'<dt>{id.blinding_type.name}</dt><dd>{id.pseudo_random_id.full_code}</dd>' for id in ids]) +
                '</dl>'
            ),'success')

    return redirect(url_for("ui.study", id=study.id))


@blueprint.route("/study/<int:id>/unblinding/", methods=['POST'])
@assert_study_user()
def unblinding(id):
    study = Study.query.get_or_404(id)

    un_blinding_form = UnblindingForm()

    if un_blinding_form.validate_on_submit():
        print(un_blinding_form.id.data)
        blinding = Blinding.query.join(PseudoRandomId).filter_by(full_code=un_blinding_form.id.data).first()
        print(blinding)

        if blinding is None or blinding.blinding_type.blinding_set.study != study:
            flash(
                'Blind ID "{}" not found for study {}'.format(
                    un_blinding_form.id.data,
                    study.name,
                ),
                'warning',
            )
        else:
            flash(
                '{} {} ID "{}" is unblinded to "{}"'.format(
                    blinding.blinding_type.blinding_set.name,
                    blinding.blinding_type.name,
                    blinding.pseudo_random_id.full_code,
                    blinding.unblind_id,
                ),
                'success',
            )

    return redirect(url_for("ui.study", id=study.id))


@blueprint.route("/study/<int:id>")
@blueprint.route('/study/<int:id>?page=<int:page>')
@assert_study_user()
def study(id, page=1):
    study = Study.query.get_or_404(id)
    blinding_form = None
    unblinding_form = None

    if study.blinding_sets:
        blinding_form = BlindingForm()
        unblinding_form = UnblindingForm()

    participants = StudyParticipant.query.filter_by(study_id=id).paginate(
        page=page,
        per_page=10,
        error_out=False,
    )

    return render_template(
        "ui/study.html",
        study=study,
        blinding_form=blinding_form,
        unblinding_form=unblinding_form,
        participants=participants,
    )
