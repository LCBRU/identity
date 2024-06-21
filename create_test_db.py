#!/usr/bin/env python3

from itertools import cycle
from random import randint, choice
from dotenv import load_dotenv
from lbrc_flask.database import db
from lbrc_flask.security import init_roles, init_users
from sqlalchemy import select
from identity.model import Study
from identity.model.blinding import BlindingType
from identity.model.edge import EdgeSiteStudy
from identity.model.civicrm import (
    CiviCrmParticipantAmazeDetails,
    CiviCrmParticipantArchiveDetails,
    CiviCrmParticipantBioresourceDetails,
    CiviCrmParticipantBioresourceSubStudyDetails,
    CiviCrmParticipantBioresourceWithdrawalDetails,
    CiviCrmParticipantBraveDetails,
    CiviCrmParticipantBriccsDetails,
    CiviCrmParticipantCardiometDetails,
    CiviCrmParticipantDiscordanceDetails,
    CiviCrmParticipantDreamDetails,
    CiviCrmParticipantEmmace4Details,
    CiviCrmParticipantFastDetails,
    CiviCrmParticipantFoamiDetails,
    CiviCrmParticipantGenvascDetails,
    CiviCrmParticipantGenvascInvoiceDetails,
    CiviCrmParticipantGenvascWithdrawalDetails,
    CiviCrmParticipantGlobalLeadersDetails,
    CiviCrmParticipantGraphic2Details,
    CiviCrmParticipantIndapamideDetails,
    CiviCrmParticipantIntervalDetails,
    CiviCrmParticipantLentenDetails,
    CiviCrmParticipantLimbDetails,
    CiviCrmParticipantNationalBioresourceDetails,
    CiviCrmParticipantOmicsDetails,
    CiviCrmParticipantPredictDetails,
    CiviCrmParticipantPreeclampsiaDetails,
    CiviCrmParticipantScadDetails,
    CiviCrmParticipantScadRegisterDetails,
    CiviCrmParticipantSpiralDetails,
    CiviCrmParticipantTmaoDetails,
    CiviCrmStudy,
    CiviCrmParticipant,
    CiviCrmContact,
    CiviCrmParticipantContact,
    CiviCrmGender,
    CiviCrmCaseStatus,
    CiviCrmContactIds,
)
from identity.model.id import PseudoRandomIdProvider
from identity.printing import LabelBundle
from identity.setup import setup_data
from faker import Faker
fake = Faker()

load_dotenv()

from identity import create_app

application = create_app()
application.app_context().push()
db.create_all()
init_roles([])
init_users()

setup_data()

study_names = [
    'Amaze',
    'Bioresource',
    'Brave',
    'BRICCS',
    'Cardiomet',
    'Discordance',
    'Dream',
    'EMMACE 4',
    'FAST',
    'FOAMI',
    'GENVASC',
    'Global Leaders',
    'Graphic 2',
    'Indapamide',
    'Interval',
    'Lenten',
    'LIMB',
    'National Bioresource',
    'OMICS',
    'Predict',
    'Preeclampsia',
    'SCAD',
    'SPIRAL',
    'TMAO',
]
primary_clinical_management_areas = cycle([fake.word().title() for _ in range(13)])
status = cycle(['Cancel', 'Loaded', 'Deleted'])
principle_investigator = cycle(fake.name() for _ in range(5))
lead_nurse = cycle(fake.name() for _ in range(5))


# CiviCRM Gender
genders = [
    CiviCrmGender(value=1, name='Female', label='Female'),
    CiviCrmGender(value=2, name='Male', label='Male'),
]
db.session.add_all(genders)
db.session.commit()


# CiviCRM Case Status
case_statuses = [
    CiviCrmCaseStatus(value=1, name='Open', label='Open'),
    CiviCrmCaseStatus(value=2, name='Closed', label='Closed'),
    CiviCrmCaseStatus(value=3, name='Recruitment Pending', label='Recruitment Pending'),
    CiviCrmCaseStatus(value=4, name='Recruited', label='Recruited'),
    CiviCrmCaseStatus(value=5, name='Available for Cohort', label='Available for Cohort'),
]
db.session.add_all(case_statuses)
db.session.commit()


# CiviCRM Studies
civicrm_studies = [CiviCrmStudy(
    name=s,
    title=s,
    description=fake.sentence(),
    is_active=True,
) for s in study_names]

db.session.add_all(civicrm_studies)
db.session.commit()


# CiviCRM Participants
civicrm_participants = []

for cs in civicrm_studies:
    civicrm_participants.extend([
        CiviCrmParticipant(
            study_id=cs.id,
            subject=fake.license_plate(),
            start_date=fake.date_object(),
            end_date=fake.date_object(),
            status_id=choice(case_statuses).value,
            is_deleted=(randint(1, 10) > 9),
    ) for _ in range(randint(15, 25))])

db.session.add_all(civicrm_participants)
db.session.commit()


# CiviCRM Contacts
civicrm_contacts = []
civicrm_participant_contacts = []

for cp in civicrm_participants:
    c = CiviCrmContact(
        contact_type='Subject',
        contact_sub_type='Subject',
        first_name=fake.first_name(),
        middle_name=fake.first_name(),
        last_name=fake.last_name(),
        gender_id=choice(genders).value,
        birth_date=fake.date(),
        is_deleted=(randint(1, 10) > 9),
    )
    civicrm_contacts.append(c)
    civicrm_participant_contacts.append(
        CiviCrmParticipantContact(
            participant=cp,
            contact=c,
        ))

db.session.add_all(civicrm_contacts)
db.session.add_all(civicrm_participant_contacts)
db.session.commit()

contact_ids = []

for c in civicrm_contacts:
    contact_ids.append(CiviCrmContactIds(
        entity_id=c.id,
        nhs_number=f'{fake.pyint(1000000000, 9999999999)}',
        uhl_system_number=f'S{fake.pyint(1000000, 9999999)}',
    ))

db.session.add_all(contact_ids)
db.session.commit()


# Study Custom Details
participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'AMAZE'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantAmazeDetails(
        entity_id=p.id,
        study_identifier=f'AM{fake.pyint(10000, 99999)}',
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'Bioresource'))).scalars()
for p in participants:
    for _ in range(randint(1,3)):
        db.session.add(CiviCrmParticipantBioresourceSubStudyDetails(
            entity_id=p.id,
            sub_study=fake.word().title(),
        ))
    db.session.add(CiviCrmParticipantBioresourceDetails(
        entity_id=p.id,
        study_identifier=f'Br{fake.pyint(10000, 99999)}',
        date_of_consent=fake.date_time(),
        nihr_bioresource_consent_q1=choice([True, False]),
        nihr_bioresource_consent_q2=choice([True, False]),
        nihr_bioresource_consent_q3=choice([True, False]),
        nihr_bioresource_consent_q4=choice([True, False]),
        nihr_bioresource_consent_q5=choice([True, False]),
        nihr_bioresource_consent_q6=choice([True, False]),
        nihr_bioresource_legacy_id=f'LBr{fake.pyint(10000, 99999)}',
    ))
    if randint(1,10) >= 9:
        db.session.add(CiviCrmParticipantBioresourceWithdrawalDetails(
            entity_id=p.id,
            nihr_bioresource_withdrawal_stat=choice(['Keep', 'Destroy']),
        ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'Brave'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantBraveDetails(
        entity_id=p.id,
        study_identifier=f'BR{fake.pyint(10000, 99999)}',
        source_study=fake.word().title(),
        briccs_id=f'BPt{fake.pyint(10000, 99999)}',
        family_id=f'BRFm{fake.pyint(10000, 99999)}',
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'BRICCS'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantBriccsDetails(
        entity_id=p.id,
        study_identifier=f'BPt{fake.pyint(10000, 99999)}',
        interview_date_and_time=fake.date_time(),
        interviewer=fake.name(),
        interview_status=choice(['Good', 'Bad', 'Indifferent']),
        consent_understands_consent=choice([True, False]),
        consent_blood_and_urine=choice([True, False]),
        consent_briccs_database=choice([True, False]),
        consent_further_contact=choice([True, False]),
        consent_understands_withdrawal=choice([True, False]),
        recruitment_type=choice(['Index', 'Healthy Volunteer']),
        invitation_for=choice(['Sutin', 'Nustin']),
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'Cardiomet'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantCardiometDetails(
        entity_id=p.id,
        study_identifier=f'Cm{fake.pyint(10000, 99999)}',
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'Discordance'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantDiscordanceDetails(
        entity_id=p.id,
        study_identifier=f'Dis{fake.pyint(10000, 99999)}',
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'Dream'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantDreamDetails(
        entity_id=p.id,
        study_identifier=f'DR{fake.pyint(10000, 99999)}',
        consent_to_participate_in_dream=choice([True, False]),
        consent_to_store_dream_study_sam=choice([True, False]),
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'EMMACE 4'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantEmmace4Details(
        entity_id=p.id,
        study_identifier=f'Em{fake.pyint(10000, 99999)}',
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'FAST'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantFastDetails(
        entity_id=p.id,
        study_identifier=f'Fs{fake.pyint(10000, 99999)}',
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'FOAMI'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantFoamiDetails(
        entity_id=p.id,
        study_identifier=f'Fo{fake.pyint(10000, 99999)}',
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'GENVASC'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantGenvascInvoiceDetails(
        entity_id=p.id,
        invoice_year=f'{fake.pyint(2015, 2020)}',
        invoice_quarter=f'Q{fake.pyint(1, 4)}',
        processed_by=fake.name(),
        processed_date=fake.date_time(),
        reimbursed_status=choice(['Reimbursed', 'Duplicate', 'Error']),
        notes=fake.paragraph(),
    ))
    db.session.add(CiviCrmParticipantGenvascDetails(
        entity_id=p.id,
        study_identifier=f'GPt{fake.pyint(10000, 99999)}',
        consent_q1=choice([True, False]),
        consent_q2=choice([True, False]),
        consent_q3=choice([True, False]),
        consent_q4=choice([True, False]),
        consent_q5=choice([True, False]),
        consent_q6=choice([True, False]),
        consent_q7=choice([True, False]),
        post_code=fake.postcode(),
    ))
    if randint(1,10) >= 9:
        db.session.add(CiviCrmParticipantGenvascWithdrawalDetails(
            entity_id=p.id,
            withdrawal_status=choice(['Keep', 'Destroy']),
        ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'Global Leaders'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantGlobalLeadersDetails(
        entity_id=p.id,
        study_identifier=f'GL{fake.pyint(10000, 99999)}',
        treatment_arm=choice('ABC'),
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'Graphic 2'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantGraphic2Details(
        entity_id=p.id,
        study_identifier=f'Gfx{fake.pyint(10000, 99999)}',
        graphic_lab_id=f'GfxL{fake.pyint(10000, 99999)}',
        graphic_family_id=f'GfxF{fake.pyint(10000, 99999)}',
        consent_for_further_studies=choice([True, False]),
        g1_blood_consent=choice([True, False]),
        pre_consent_to_graphic_2=choice([True, False]),
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'Indapamide'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantIndapamideDetails(
        entity_id=p.id,
        study_identifier=f'Ind{fake.pyint(10000, 99999)}',
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'Interval'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantIntervalDetails(
        entity_id=p.id,
        study_identifier=f'Int{fake.pyint(10000, 99999)}',
        consent_date=fake.date(),
        consent_version=choice(['v1', 'v2', 'v3']),
        consent_leaflet=choice(['v1', 'v2']),
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'Lenten'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantLentenDetails(
        entity_id=p.id,
        study_identifier=f'Len{fake.pyint(10000, 99999)}',
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'LIMB'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantLimbDetails(
        entity_id=p.id,
        study_identifier=f'Lmb{fake.pyint(10000, 99999)}',
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'National Bioresource'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantNationalBioresourceDetails(
        entity_id=p.id,
        study_identifier=f'NBr{fake.pyint(10000, 99999)}',
        leicester_bioresource_id=f'Br{fake.pyint(10000, 99999)}',
        legacy_bioresource_id=f'LBr{fake.pyint(10000, 99999)}',
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'OMICS'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantOmicsDetails(
        entity_id=p.id,
        study_identifier=f'Om{fake.pyint(10000, 99999)}',
        sample_source_study=fake.word().title(),
        failed_qc=choice([True, False]),
        date_data_received=fake.date_time(),
        omics_type=choice(['Full', 'Panel']),
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'Predict'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantPredictDetails(
        entity_id=p.id,
        study_identifier=f'Pr{fake.pyint(10000, 99999)}',
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'Preeclampsia'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantPreeclampsiaDetails(
        entity_id=p.id,
        study_identifier=f'Pre{fake.pyint(10000, 99999)}',
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'SCAD'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantScadDetails(
        entity_id=p.id,
        study_identifier=f'Sc{fake.pyint(10000, 99999)}',
        consent_read_information=choice([True, False]),
        consent_understands_withdrawal=choice([True, False]),
        consent_provide_medical_informat=choice([True, False]),
        consent_contact_by_research_team=choice([True, False]),
        consent_sample_storage=choice([True, False]),
        consent_no_financial_benefit=choice([True, False]),
        consent_contact_gp=choice([True, False]),
        consent_dna_sequencing=choice([True, False]),
        consent_skin_biopsy=choice([True, False]),
        consent_understands_how_to_conta=choice([True, False]),
        consent_share_information_with_m=choice([True, False]),
        consent_access_to_medical_record=choice([True, False]),
        consent_contact_for_related_stud=choice([True, False]),
        consent_receive_research_sumary=choice([True, False]),
        consent_date=fake.date_time(),
        briccs_id=f'Br{fake.pyint(10000, 99999)}',
        survey_reference=f'ScR{fake.pyint(10000, 99999)}',
        scad_visit_id=f'ScV{fake.pyint(10000, 99999)}',
        recruitment_type=choice(['Index', 'Healthy Volunteer']),
        second_scad_survey_id=f'ScR{fake.pyint(10000, 99999)}',
        scad_registry_id=f'ScRef{fake.pyint(10000, 99999)}',
        family_id=f'ScFm{fake.pyint(10000, 99999)}',
    ))
    db.session.add(CiviCrmParticipantScadRegisterDetails(
        entity_id=p.id,
        scad_registry_id_131=f'ScRef{fake.pyint(10000, 99999)}',
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'SPIRAL'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantSpiralDetails(
        entity_id=p.id,
        study_identifier=f'Spi{fake.pyint(10000, 99999)}',
    ))

participants = db.session.execute(select(CiviCrmParticipant).where(CiviCrmParticipant.study.has(CiviCrmStudy.name == 'TMAO'))).scalars()
for p in participants:
    db.session.add(CiviCrmParticipantTmaoDetails(
        entity_id=p.id,
        study_identifier=f'Tm{fake.pyint(10000, 99999)}',
        tmao_consent_has_read_informatio=choice([True, False]),
        tmao_consent_understands_withdra=choice([True, False]),
        tmao_consent_permission_to_acces=choice([True, False]),
        tmao_consent_gp_informed=choice([True, False]),
        tmao_consent_to_enrol=choice([True, False]),
        tmao_consent_to_store_blood=choice([True, False]),
    ))

db.session.commit()

# Archiving

participants = db.session.execute(select(CiviCrmParticipant)).scalars()
for p in participants:
    if choice([True, False]):
        db.session.add(CiviCrmParticipantArchiveDetails(
            entity_id=p.id,
            box_barcode=f'Arxiv{fake.pyint(10000, 99999)}',
        ))
db.session.commit()


# Edge Studies
edge_studies = [EdgeSiteStudy(
    project_id=fake.ean(length=8),
    iras_number=fake.license_plate(),
    project_short_title=s,
    primary_clinical_management_areas=next(primary_clinical_management_areas),
    project_site_status=next(status),
    principal_investigator=next(principle_investigator),
    project_site_lead_nurses=next(lead_nurse),
) for s in study_names]

db.session.add_all(edge_studies)
db.session.commit()


# Studies
studies = [Study(name=es.project_short_title, edge_id=es.project_id, civicrm_study_id=cs.id) for es, cs in zip(edge_studies, civicrm_studies)]

db.session.add_all(studies)
db.session.commit()


# Labels
disable_batch_printing=cycle([True, False])
user_defined_participant_id=cycle([True, False, False])
bundles = []
for s in studies:
    bundles.extend([LabelBundle(
        name=f'{s.name} {i}',
        study_id=s.id,
        disable_batch_printing=next(disable_batch_printing),
        user_defined_participant_id=next(user_defined_participant_id),
    ) for i in range(1, randint(1, 5))])

db.session.add_all(bundles)
db.session.commit()


# Blinding
blinding_types = []
for s in studies:

    blinding_types.extend([BlindingType(
        name=f'{s.name} {i}',
        study_id=s.id,
        pseudo_random_id_provider=PseudoRandomIdProvider(
            name=fake.word().title(),
            prefix=fake.word()[0:3].upper(),
        ),

    ) for i in range(1, randint(1, 5))])

db.session.add_all(blinding_types)
db.session.commit()


db.session.close()
