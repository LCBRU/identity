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
from ..decorators import assert_study_user
from ..forms import LabelDefinition
from lbrc_flask.response import refresh_response


@blueprint.route("/labels/")
def labels():
    return render_template(
        "ui/labels.html",
        studies=current_user.studies,
    )


@blueprint.route("/label_bundle/<int:label_bundle_id>/print/<int:count>")
@assert_study_user()
def label_bundle_print(label_bundle_id, count=1):
    label_bundle = LabelBundle.query.get_or_404(label_bundle_id)

    if label_bundle.user_defined_participant_id:
        return redirect(url_for("ui.label_bundle_definition", label_bundle_id=label_bundle_id, count=count))

    print_label_bundle(count, label_bundle)
    return refresh_response()


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


@blueprint.route("/label_bundle/<int:label_bundle_id>/define/<int:count>", methods=['GET', 'POST'])
@assert_study_user()
def label_bundle_definition(label_bundle_id, count=1):
    label_bundle = db.get_or_404(LabelBundle, label_bundle_id)
    form = LabelDefinition()

    if form.validate_on_submit():
        label_bundle.set_participant_id(form.participant_id.data)
        print_label_bundle(count, label_bundle)
        return refresh_response()

    return render_template(
        "lbrc/form_modal.html",
        title=f'Enter Participant Identifier',
        form=form,
        submit_label='Print',
        url=url_for('ui.label_bundle_definition', label_bundle_id=label_bundle_id, count=count),
    )
