import traceback
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    current_app,
)
from flask_login import current_user
from identity.printing import LabelBundle
from .. import blueprint, db
from ..decorators import assert_can_print_study_label
from lbrc_flask.response import refresh_response
from lbrc_flask.forms import FlashingForm
from wtforms import HiddenField, StringField, SelectField
from wtforms.validators import Length, DataRequired


@blueprint.route("/labels/")
def labels():
    if len(current_user.studies) == 1:
        return redirect(url_for('ui.study', id=current_user.studies[0].id))
    else:
        return redirect(url_for('ui.index'))


def print_label_bundle(count, label_bundle):
    try:
        labels = label_bundle.get_labels(count)
        db.session.commit()

        for l in labels:
            l.print()

        flash('Labels have been sent to the printer')
    except:
        current_app.logger.error(traceback.format_exc())
        flash("An error occurred while printing.  Check that the printer has paper and ink, and that a jam has not occurred.", "error")


@blueprint.route("/label_bundle/<int:id>/print", methods=['GET', 'POST'])
@assert_can_print_study_label()
def label_bundle_definition(id):
    label_bundle = db.get_or_404(LabelBundle, id)
    form = get_label_definition_form(label_bundle=label_bundle)

    if form.validate_on_submit():
        if form.has_value('participant_id'):
            label_bundle.set_participant_id(form.participant_id.data)
        if form.has_value('count'):
            count = form.count.data
        else:
            count = 1
        print_label_bundle(count, label_bundle)
        return refresh_response()

    return render_template(
        "lbrc/form_modal.html",
        title=f'Print {label_bundle.name} Labels',
        form=form,
        submit_label='Print',
        url=url_for('ui.label_bundle_definition', id=id),
    )


def get_label_definition_form(label_bundle):

    class LabelDefinition(FlashingForm):
            pass

    if label_bundle.user_defined_participant_id:
        setattr(LabelDefinition, 'participant_id', StringField("Participant Identifier", validators=[DataRequired(), Length(max=100)]))
    
    if not label_bundle.disable_batch_printing:
        setattr(LabelDefinition, 'count', SelectField('Label Count', coerce=int, choices=[1, 5, 10, 50]))

    result = LabelDefinition()

    return result
