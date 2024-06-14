from sqlalchemy import and_, or_, select
from lbrc_flask.database import db
from identity.model.civicrm import CiviCrmCaseStatus, CiviCrmContact, CiviCrmContactIds, CiviCrmParticipantAmazeDetails, CiviCrmParticipantArchiveDetails, CiviCrmParticipantBioresourceDetails, CiviCrmParticipantBraveDetails, CiviCrmParticipantBriccsDetails, CiviCrmParticipantCardiometDetails, CiviCrmParticipantContact, CiviCrmParticipantDiscordanceDetails, CiviCrmParticipantDreamDetails, CiviCrmParticipantEmmace4Details, CiviCrmParticipantFastDetails, CiviCrmParticipantFoamiDetails, CiviCrmParticipantGenvascDetails, CiviCrmParticipantGlobalLeadersDetails, CiviCrmParticipantGraphic2Details, CiviCrmParticipantIndapamideDetails, CiviCrmParticipantIntervalDetails, CiviCrmParticipantLentenDetails, CiviCrmParticipantLimbDetails, CiviCrmParticipantNationalBioresourceDetails, CiviCrmParticipantOmicsDetails, CiviCrmParticipantPredictDetails, CiviCrmParticipantPreeclampsiaDetails, CiviCrmParticipantScadDetails, CiviCrmParticipantScadRegisterDetails, CiviCrmParticipantSpiralDetails, CiviCrmParticipantTmaoDetails, CiviCrmStudy, CiviCrmParticipant
from lbrc_flask.forms import SearchForm
from wtforms import BooleanField


class ParticipantSearchForm(SearchForm):
    show_deleted = BooleanField('Deleted')


def get_civicrm_study_choices():
    q = select(CiviCrmStudy).where(CiviCrmStudy.is_active == True).order_by(CiviCrmStudy.name)
    return [(s.id, s.name) for s in db.session.execute(q).scalars()]


def get_civicrm_study_status_choices():
    q = select(CiviCrmCaseStatus).where(CiviCrmCaseStatus.is_active == True).order_by(CiviCrmCaseStatus.name)
    return [(s.value, s.name) for s in db.session.execute(q).scalars()]


def get_participant_query(form, study_id):
    q = select(CiviCrmParticipant).where(CiviCrmParticipant.study_id == study_id)

    if form.has_value('search'):
        and_wheres = []
        for s in form.search.data.split():
            or_wheres = []
            or_wheres.append(
                CiviCrmParticipant.participant_contacts.any(
                    CiviCrmParticipantContact.contact.has(or_(
                        CiviCrmContact.first_name.like(f'%{s}%'),
                        CiviCrmContact.last_name.like(f'%{s}%'),
                    )
                )))
            or_wheres.append(
                CiviCrmParticipant.participant_contacts.any(
                    CiviCrmParticipantContact.contact.has(
                        CiviCrmContact.contact_ids.has(or_(
                            CiviCrmContactIds.nhs_number == s,
                            CiviCrmContactIds.uhl_system_number == s,
                        )))))
            or_wheres.append(
                CiviCrmParticipant.id.in_(participant_ids_from_identifiers(s, study_id))
            )
            and_wheres.append(or_(*or_wheres))
        q = q.where(and_(*and_wheres))

    if not form.show_deleted.data:
        q = q.where(CiviCrmParticipant.is_deleted == False)

    return q


def participant_ids_from_identifiers(search_term, study_id):
    entity_ids = []

    entity_ids.extend(db.session.execute(select(CiviCrmParticipantAmazeDetails.entity_id).where(
        CiviCrmParticipantAmazeDetails.study_identifier == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantArchiveDetails.entity_id).where(
        CiviCrmParticipantArchiveDetails.box_barcode == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantBraveDetails.entity_id).where(or_(
        CiviCrmParticipantBraveDetails.study_identifier == search_term,
        CiviCrmParticipantBraveDetails.briccs_id == search_term,
        CiviCrmParticipantBraveDetails.family_id == search_term,
    ))).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantBriccsDetails.entity_id).where(
        CiviCrmParticipantBriccsDetails.study_identifier == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantCardiometDetails.entity_id).where(
        CiviCrmParticipantCardiometDetails.study_identifier == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantDiscordanceDetails.entity_id).where(
        CiviCrmParticipantDiscordanceDetails.study_identifier == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantDreamDetails.entity_id).where(
        CiviCrmParticipantDreamDetails.study_identifier == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantEmmace4Details.entity_id).where(
        CiviCrmParticipantEmmace4Details.study_identifier == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantFastDetails.entity_id).where(
        CiviCrmParticipantFastDetails.study_identifier == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantFoamiDetails.entity_id).where(
        CiviCrmParticipantFoamiDetails.study_identifier == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantGenvascDetails.entity_id).where(
        CiviCrmParticipantGenvascDetails.study_identifier == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantGlobalLeadersDetails.entity_id).where(
        CiviCrmParticipantGlobalLeadersDetails.study_identifier == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantGraphic2Details.entity_id).where(or_(
        CiviCrmParticipantGraphic2Details.study_identifier == search_term,
        CiviCrmParticipantGraphic2Details.graphic_lab_id == search_term,
        CiviCrmParticipantGraphic2Details.graphic_family_id == search_term,
    ))).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantIndapamideDetails.entity_id).where(
        CiviCrmParticipantIndapamideDetails.study_identifier == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantIntervalDetails.entity_id).where(
        CiviCrmParticipantIntervalDetails.study_identifier == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantLentenDetails.entity_id).where(
        CiviCrmParticipantLentenDetails.study_identifier == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantLimbDetails.entity_id).where(
        CiviCrmParticipantLimbDetails.study_identifier == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantNationalBioresourceDetails.entity_id).where(or_(
        CiviCrmParticipantNationalBioresourceDetails.study_identifier == search_term,
        CiviCrmParticipantNationalBioresourceDetails.leicester_bioresource_id == search_term,
        CiviCrmParticipantNationalBioresourceDetails.legacy_bioresource_id == search_term,
    ))).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantBioresourceDetails.entity_id).where(or_(
        CiviCrmParticipantBioresourceDetails.study_identifier == search_term,
        CiviCrmParticipantBioresourceDetails.nihr_bioresource_legacy_id == search_term,
    ))).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantOmicsDetails.entity_id).where(
        CiviCrmParticipantOmicsDetails.study_identifier == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantPredictDetails.entity_id).where(
        CiviCrmParticipantPredictDetails.study_identifier == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantPreeclampsiaDetails.entity_id).where(
        CiviCrmParticipantPreeclampsiaDetails.study_identifier == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantScadDetails.entity_id).where(or_(
        CiviCrmParticipantScadDetails.study_identifier == search_term,
        CiviCrmParticipantScadDetails.briccs_id == search_term,
        CiviCrmParticipantScadDetails.survey_reference == search_term,
        CiviCrmParticipantScadDetails.scad_visit_id == search_term,
        CiviCrmParticipantScadDetails.second_scad_survey_id == search_term,
        CiviCrmParticipantScadDetails.scad_registry_id == search_term,
        CiviCrmParticipantScadDetails.family_id == search_term,
    ))).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantScadRegisterDetails.entity_id).where(
        CiviCrmParticipantScadRegisterDetails.study_identifier == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantSpiralDetails.entity_id).where(
        CiviCrmParticipantSpiralDetails.study_identifier == search_term
    )).scalars())
    entity_ids.extend(db.session.execute(select(CiviCrmParticipantTmaoDetails.entity_id).where(
        CiviCrmParticipantTmaoDetails.study_identifier == search_term
    )).scalars())

    return list(db.session.execute(select(CiviCrmParticipant.id).where(CiviCrmParticipant.study_id == study_id).where(CiviCrmParticipant.id.in_(entity_ids))).scalars())
