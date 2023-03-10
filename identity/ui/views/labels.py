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


@blueprint.route("/labels/")
def labels():
    return render_template(
        "ui/labels.html",
        studies=current_user.studies,
    )


def redirect_to_referrer(referrer, study_id):
    if referrer == 'study' and study_id is not None:
        return url_for('ui.study', id=study_id)
    else:
        return url_for("ui.labels")


@blueprint.route("/labels/study/<int:study_id>/label_bundle/<int:label_bundle_id>/print/<int:count>/referrer/<string:referrer>")
@assert_study_user()
def label_bundle_print(label_bundle_id, referrer, study_id, count=1):
    label_bundle = LabelBundle.query.get_or_404(label_bundle_id)

    if label_bundle.user_defined_participant_id:
        return redirect(url_for("ui.label_bundle_definition", label_bundle_id=label_bundle_id, referrer=referrer, study_id=study_id, count=count))

    return print_label_bundle(referrer, study_id, count, label_bundle)


def print_label_bundle(referrer, study_id, count, label_bundle):
    try:
        labels = label_bundle.get_labels(count)
        db.session.commit()

        for l in labels:
            l.print()

        flash('Labels have been sent to the printer')
    except:
        current_app.logger.error(traceback.format_exc())
        flash("An error occurred while printing.  Check that the printer has paper and ink, and that a jam has not occurred.", "error")
    finally:
        return redirect(redirect_to_referrer(referrer, study_id))


@blueprint.route("/labels/study/<int:study_id>/label_bundle/<string:label_bundle_id>/define/<int:count>/referrer/<string:referrer>", methods=['GET', 'POST'])
@assert_study_user()
def label_bundle_definition(label_bundle_id, referrer, study_id, count=1):
    label_bundle = LabelBundle.query.get_or_404(label_bundle_id)
    form = LabelDefinition()

    if form.validate_on_submit():
        label_bundle.set_participant_id(form.participant_id.data)
        return print_label_bundle(referrer, study_id, count, label_bundle)

    return render_template(
        "ui/label_bundle_definition.html",
        form=form,
        label_bundle=label_bundle,
        study_id=study_id,
        referrer=referrer,
        count=count,
        back=f'ui.{referrer}',
        backparams={'id': study_id},
    )
