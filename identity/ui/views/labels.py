import time
import traceback
from itertools import chain
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    current_app,
    abort,
)
from flask_login import current_user
from identity.printing.model import LabelPack
from .. import blueprint, db
from ..decorators import assert_study_user
from ..forms import LabelDefinition


@blueprint.route("/labels/")
def labels():
    return render_template(
        "ui/labels.html",
        label_sets=chain.from_iterable(s.label_packs for s in current_user.studies),
        studies=current_user.studies,
    )


@blueprint.route("/labels/study/<int:study_id>/<string:pack_name>/print/<int:count>/referrer/<string:referrer>")
@assert_study_user()
def label_print(pack_name, referrer, study_id, count=1):
    label_pack = LabelPack.query.filter_by(type=pack_name).one()

    if label_pack.user_defined_participant_id():
        return redirect(url_for("ui.label_print_definition", pack_name=pack_name, referrer=referrer, study_id=study_id, count=count))

    try:
        label_pack.print(count)
        flash('Labels have been sent to the printer')
    except:
        current_app.logger.error(traceback.format_exc())
        flash("An error occurred while printing.  Check that the printer has paper and ink, and that a jam has not occurred.", "error")
    finally:
        return redirect(redirect_to_referrer(referrer, study_id))


@blueprint.route("/labels/study/<int:study_id>/<string:pack_name>/define/<int:count>/referrer/<string:referrer>", methods=['GET', 'POST'])
@assert_study_user()
def label_print_definition(pack_name, referrer, study_id, count=1):
    label_pack = LabelPack.query.filter_by(type=pack_name).one()
    form = LabelDefinition()

    if form.validate_on_submit():

        try:
            label_pack.set_participant_id(form.participant_id.data)
            label_pack.print(count)
            flash('Labels have been sent to the printer')
        except:
            current_app.logger.error(traceback.format_exc())
            flash("An error occurred while printing.  Check that the printer has paper and ink, and that a jam has not occurred.", "error")
        finally:
            return redirect(redirect_to_referrer(referrer, study_id))

    return render_template(
        "ui/label_definition.html",
        form=form,
        label_pack=label_pack,
        study_id=study_id,
        pack_name=pack_name,
        referrer=referrer,
        count=count,
        back=f'ui.{referrer}',
        backparams={'id': study_id},
    )


def redirect_to_referrer(referrer, study_id):
    if referrer == 'study' and study_id is not None:
        return url_for('ui.study', id=study_id)
    else:
        return url_for("ui.labels")
