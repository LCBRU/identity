from sqlalchemy import func
from flask import render_template, redirect
from flask.helpers import url_for
from flask_security import roles_required
from identity.ecrfs.model import EcrfDetail, EcrfParticipantIdentifierSource
from identity.model.id import ParticipantIdentifierSource, participant_identifiers__participant_identifier_sources
from lbrc_flask.database import db
from sqlalchemy import select, func, and_, delete
from .. import blueprint


@blueprint.route("/imports")
@roles_required('admin')
def imports():
    ecrf_count = EcrfDetail.query.count()

    return render_template("ui/imports.html", ecrf_count=ecrf_count)


@blueprint.route("/delete_ecrfs", methods=['POST'])
@roles_required('admin')
def delete_ecrfs():
    epis = EcrfParticipantIdentifierSource.__table__
    pis = ParticipantIdentifierSource.__table__
    pipis = participant_identifiers__participant_identifier_sources

    with db.engine.connect() as conn:
        epis_q = select(epis.c.participant_identifier_source_id)

        epis_ids = [id for id in conn.execute(epis_q).scalars()]

        conn.execute(delete(pipis).where(pipis.c.participant_identifier_source_id.in_(epis_ids)))
        conn.execute(delete(pis).where(pis.c.id.in_(epis_ids)))
        conn.execute(delete(epis).where(epis.c.participant_identifier_source_id.in_(epis_ids)))

        EcrfDetail.query.delete()

    db.session.commit()

    return redirect(url_for('ui.imports'))
