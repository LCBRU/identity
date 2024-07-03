from itertools import chain
from lbrc_flask.database import db
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref
from sqlalchemy import Boolean, Integer, String, Date, DateTime, select
from sqlalchemy.ext.declarative import AbstractConcreteBase
from datetime import date
from cachetools import cached, TTLCache


class CiviCrmContactIds(db.Model):
    __tablename__ = 'civicrm_value_contact_ids_1'
    __bind_key__ = 'civicrm'

    id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    nhs_number: Mapped[str] = mapped_column('nhs_number_1', String(500), nullable=True)
    uhl_system_number: Mapped[str] = mapped_column('uhl_s_number_2', String(500), nullable=True)


class CiviCrmOptionValue(db.Model):
    __tablename__ = 'civicrm_option_value'
    __bind_key__ = 'civicrm'

    __mapper_args__ = {
        "polymorphic_on": "option_group_id",
    }

    id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True)
    option_group_id: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str] = mapped_column(String(500), nullable=True)
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class CiviCrmGender(CiviCrmOptionValue):
    __mapper_args__ = {
        "polymorphic_identity": 3,
    }


class CiviCrmCaseStatus(CiviCrmOptionValue):
    __mapper_args__ = {
        "polymorphic_identity": 27,
    }


class CiviCrmStudy(db.Model):
    __tablename__ = 'civicrm_case_type'
    __bind_key__ = 'civicrm'

    id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)


class CiviCrmParticipantDetails(AbstractConcreteBase, db.Model):
    __bind_key__ = 'civicrm'
    id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)


class CiviCrmParticipantAmazeDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_amaze_23'
    __bind_key__ = 'civicrm'

    study_identifier: Mapped[str] = mapped_column('amaze_id_104', String(255), nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {}

    def consents(self):
        return {}


class CiviCrmParticipantArchiveDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_archiving_custom_data_22'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    box_barcode: Mapped[str] = mapped_column('archiving_box_barcode_103', String(255), nullable=True)

    def identifiers(self):
        return {'Box Barcode': self.box_barcode}

    def other(self):
        return {}

    def consents(self):
        return {}


class CiviCrmParticipantBioresourceSubStudyDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_bioresource_sub_study_28'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    sub_study: Mapped[str] = mapped_column('sub_study_118', String(255), nullable=True)

    def identifiers(self):
        return {}

    def other(self):
        return {'Sub-Study': self.sub_study}

    def consents(self):
        return {}


class CiviCrmParticipantBraveDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_brave_16'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('brave_id_74', String(255), nullable=True)
    source_study: Mapped[str] = mapped_column('brave_source_study_75', String(255), nullable=True)
    briccs_id: Mapped[str] = mapped_column('briccs_id_86', String(255), nullable=True)
    family_id: Mapped[str] = mapped_column('brave_family_id_87', String(255), nullable=True)

    def identifiers(self):
        return {
            'Study Identifier': self.study_identifier,
            'BRICCS ID': self.briccs_id,
            'Family ID': self.family_id,
            }

    def other(self):
        return {'Source Study': self.source_study}

    def consents(self):
        return {}


class CiviCrmParticipantBriccsDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_briccs_recruitment_data_10'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('briccs_id_31', String(255), nullable=True)
    interview_date_and_time: Mapped[datetime] = mapped_column('interview_date_and_time_32', DateTime, nullable=True)
    interviewer: Mapped[str] = mapped_column('interviewer_33', String(255), nullable=True)
    interview_status: Mapped[str] = mapped_column('interview_status_34', String(255), nullable=True)
    consent_understands_consent: Mapped[bool] = mapped_column('consent_understands_consent_35', Boolean, nullable=True)
    consent_blood_and_urine: Mapped[bool] = mapped_column('consent_blood_and_urine_36', Boolean, nullable=True)
    consent_briccs_database: Mapped[bool] = mapped_column('consent_briccs_database_37', Boolean, nullable=True)
    consent_further_contact: Mapped[bool] = mapped_column('consent_further_contact_38', Boolean, nullable=True)
    consent_understands_withdrawal: Mapped[bool] = mapped_column('consent_understands_withdrawal_39', Boolean, nullable=True)
    recruitment_type: Mapped[str] = mapped_column('recruitment_type_40', String(255), nullable=True)
    invitation_for: Mapped[str] = mapped_column('invitation_for__116', String(255), nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {
            'Interview Date': self.interview_date_and_time,
            'Interviewer': self.interviewer,
            'Interview Status': self.interview_status,
            'Recruitment Type': self.recruitment_type,
            'Invitation for': self.invitation_for,
        }

    def consents(self):
        return {
            'Undestands Consent': self.consent_understands_consent,
            'Blood & Urine': self.consent_blood_and_urine,
            'Database': self.consent_briccs_database,
            'Further Contact': self.consent_further_contact,
            'Understands Withdrawal': self.consent_understands_withdrawal,
        }


class CiviCrmParticipantCardiometDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_cardiomet_31'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('cardiomet_id_123', String(255), nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {}

    def consents(self):
        return {}


class CiviCrmParticipantDiscordanceDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_discordance_36'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('discordance_id_130', String(255), nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {}

    def consents(self):
        return {}


class CiviCrmParticipantDreamDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_dream_recruitment_data_6'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('dream_study_id_18', String(255), nullable=True)
    consent_to_participate_in_dream: Mapped[bool] = mapped_column('consent_to_participate_in_dream__19', Boolean, nullable=True)
    consent_to_store_dream_study_sam: Mapped[bool] = mapped_column('consent_to_store_dream_study_sam_20', Boolean, nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {}

    def consents(self):
        return {
            'Participate in DREAM': self.consent_to_participate_in_dream,
            'Store Study Samples': self.consent_to_store_dream_study_sam,
        }


class CiviCrmParticipantEmmace4Details(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_emmace_4_recruitment_data_13'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('emmace_4_id_50', String(255), nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {}

    def consents(self):
        return {}


class CiviCrmParticipantFastDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_fast_24'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('fast_id_106', String(255), nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {}

    def consents(self):
        return {}


class CiviCrmParticipantFoamiDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_foami_27'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('foami_id_117', String(255), nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {}

    def consents(self):
        return {}


class CiviCrmParticipantGenvascInvoiceDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_genvasc_invoice_data_25'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    invoice_year: Mapped[str] = mapped_column('invoice_year_107', String(255), nullable=True)
    invoice_quarter: Mapped[str] = mapped_column('invoice_quarter_108', String(255), nullable=True)
    processed_by: Mapped[str] = mapped_column('processed_by_110', String(255), nullable=True)
    processed_date: Mapped[datetime] = mapped_column('processed_date_111', DateTime, nullable=True)
    reimbursed_status: Mapped[str] = mapped_column('reimbursed_status_114', String(255), nullable=True)
    notes: Mapped[str] = mapped_column('notes_115', String(4000), nullable=True)

    def identifiers(self):
        return {}

    def other(self):
        return {
            'Invoice Year': self.invoice_year,
            'Invoice Quarter': self.invoice_quarter,
            'Processed By': self.processed_by,
            'Processed Date': self.processed_date,
            'Reimbursed Status': self.reimbursed_status,
            'Notes': self.notes,
        }

    def consents(self):
        return {}


class CiviCrmParticipantGenvascDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_genvasc_recruitment_data_5'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('genvasc_id_10', String(255), nullable=True)
    consent_q1: Mapped[bool] = mapped_column('genvasc_consent_q1_11', Boolean, nullable=True)
    consent_q2: Mapped[bool] = mapped_column('genvasc_consent_q2_12', Boolean, nullable=True)
    consent_q3: Mapped[bool] = mapped_column('genvasc_consent_q3_13', Boolean, nullable=True)
    consent_q4: Mapped[bool] = mapped_column('genvasc_consent_q4_14', Boolean, nullable=True)
    consent_q5: Mapped[bool] = mapped_column('genvasc_consent_q5_15', Boolean, nullable=True)
    consent_q6: Mapped[bool] = mapped_column('genvasc_consent_q6_16', Boolean, nullable=True)
    consent_q7: Mapped[bool] = mapped_column('genvasc_consent_q7_17', Boolean, nullable=True)
    post_code: Mapped[str] = mapped_column('genvasc_post_code_51', String(255), nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {'Post Code': self.post_code}

    def consents(self):
        return {
            'Question 1': self.consent_q1,
            'Question 2': self.consent_q2,
            'Question 3': self.consent_q3,
            'Question 4': self.consent_q4,
            'Question 5': self.consent_q5,
            'Question 6': self.consent_q6,
            'Question 7': self.consent_q7,
        }


class CiviCrmParticipantGenvascWithdrawalDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_genvasc_withdrawal_status_8'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    withdrawal_status: Mapped[str] = mapped_column('withdrawal_status_24', String(255), nullable=True)

    def identifiers(self):
        return {}

    def other(self):
        return {'Withdrawal Status': self.withdrawal_status}

    def consents(self):
        return {}


class CiviCrmParticipantGlobalLeadersDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_global_leaders_17'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('global_leaders_id_76', String(255), nullable=True)
    treatment_arm: Mapped[str] = mapped_column('treatment_arm_77', String(255), nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {'Treatment Arm': self.treatment_arm}

    def consents(self):
        return {}


class CiviCrmParticipantGraphic2Details(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_graphic2_9'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('graphic_participant_id_26', String(255), nullable=True)
    graphic_lab_id: Mapped[str] = mapped_column('graphic_lab_id_25', String(255), nullable=True)
    graphic_family_id: Mapped[str] = mapped_column('graphic_family_id_27', String(255), nullable=True)
    consent_for_further_studies: Mapped[bool] = mapped_column('consent_for_further_studies_28', Boolean, nullable=True)
    g1_blood_consent: Mapped[bool] = mapped_column('g1_blood_consent_29', Boolean, nullable=True)
    pre_consent_to_graphic_2: Mapped[bool] = mapped_column('pre_consent_to_graphic_2_30', Boolean, nullable=True)

    def identifiers(self):
        return {
            'Study Identifier': self.study_identifier,
            'Lab ID': self.graphic_lab_id,
            'Family ID': self.graphic_family_id,
        }

    def other(self):
        return {}

    def consents(self):
        return {
            'Further Studies': self.consent_for_further_studies,
            'Graphic 1 Blood': self.g1_blood_consent,
            'Pre-consent to Graphic 2': self.pre_consent_to_graphic_2,
        }


class CiviCrmParticipantIndapamideDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_indapamide_26'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('indapamide_id', String(255), nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {}

    def consents(self):
        return {}


class CiviCrmParticipantIntervalDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_interval_data_21'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('interval_id_98', String(255), nullable=True)
    consent_date: Mapped[date] = mapped_column('consent_date_99', Date, nullable=True)
    consent_version: Mapped[str] = mapped_column('consent_version_100', String(255), nullable=True)
    consent_leaflet: Mapped[str] = mapped_column('consent_leaflet_101', String(255), nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {}

    def consents(self):
        return {
            'Date': self.consent_date,
            'Version': self.consent_version,
            'Leaflet': self.consent_leaflet,
        }


class CiviCrmParticipantLentenDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_lenten_29'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('lenten_id_119', String(255), nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {}

    def consents(self):
        return {}


class CiviCrmParticipantLimbDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_limb_35'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('limb_id_129', String(255), nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {}

    def consents(self):
        return {}


class CiviCrmParticipantNationalBioresourceDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_national_bioresource_34'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('national_bioresource_id_126', String(255), nullable=True)
    leicester_bioresource_id: Mapped[str] = mapped_column('leicester_bioresource_id_127', String(255), nullable=True)
    legacy_bioresource_id: Mapped[str] = mapped_column('legacy_bioresource_id_128', String(255), nullable=True)

    def identifiers(self):
        return {
            'Study Identifier': self.study_identifier,
            'Leicester Bioresource ID': self.leicester_bioresource_id,
            'Legacy ID': self.legacy_bioresource_id,
        }

    def other(self):
        return {}

    def consents(self):
        return {}


class CiviCrmParticipantBioresourceDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_nihr_bioresource_11'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('nihr_bioresource_id_41', String(255), nullable=True)
    date_of_consent: Mapped[datetime] = mapped_column('date_of_consent_42', DateTime, nullable=True)
    nihr_bioresource_consent_q1: Mapped[bool] = mapped_column('nihr_bioresource_consent_q1_43', Boolean, nullable=True)
    nihr_bioresource_consent_q2: Mapped[bool] = mapped_column('nihr_bioresource_consent_q2_44', Boolean, nullable=True)
    nihr_bioresource_consent_q3: Mapped[bool] = mapped_column('nihr_bioresource_consent_q3_45', Boolean, nullable=True)
    nihr_bioresource_consent_q4: Mapped[bool] = mapped_column('nihr_bioresource_consent_q4_46', Boolean, nullable=True)
    nihr_bioresource_consent_q5: Mapped[bool] = mapped_column('nihr_bioresource_consent_q5_47', Boolean, nullable=True)
    nihr_bioresource_consent_q6: Mapped[bool] = mapped_column('nihr_bioresource_consent_q6_48', Boolean, nullable=True)
    nihr_bioresource_legacy_id: Mapped[str] = mapped_column('nihr_bioresource_legacy_id_78', String(255), nullable=True)

    def identifiers(self):
        return {
            'Study Identifier': self.study_identifier,
            'Legacy ID': self.nihr_bioresource_legacy_id,
        }

    def other(self):
        return {}

    def consents(self):
        return {
            'Date': self.date_of_consent,
            'Question 1': self.nihr_bioresource_consent_q1,
            'Question 2': self.nihr_bioresource_consent_q2,
            'Question 3': self.nihr_bioresource_consent_q3,
            'Question 4': self.nihr_bioresource_consent_q4,
            'Question 5': self.nihr_bioresource_consent_q5,
            'Question 6': self.nihr_bioresource_consent_q6,
        }


class CiviCrmParticipantBioresourceWithdrawalDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_nihr_bioresource_withdrawal_12'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    nihr_bioresource_withdrawal_stat: Mapped[str] = mapped_column('nihr_bioresource_withdrawal_stat_49', String(255), nullable=True)

    def identifiers(self):
        return {}

    def other(self):
        return {'Withdrawal Status': self.nihr_bioresource_withdrawal_stat}

    def consents(self):
        return {}


class CiviCrmParticipantOmicsDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_omics_register_20'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('omics_id_102', String(255), nullable=True)
    sample_source_study: Mapped[str] = mapped_column('sample_source_study_95', String(255), nullable=True)
    failed_qc: Mapped[bool] = mapped_column('failed_qc_96', Boolean, nullable=True)
    date_data_received: Mapped[datetime] = mapped_column('date_data_received_97', DateTime, nullable=True)
    omics_type: Mapped[str] = mapped_column('omics_type_94', String(255), nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {
            'Sample Source Study': self.sample_source_study,
            'Failed QC': self.failed_qc,
            'Date Data Received': self.date_data_received,
            'OMICS Type': self.omics_type,
        }

    def consents(self):
        return {}


class CiviCrmParticipantPredictDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_predict_30'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('predict_id_121', String(255), nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {}

    def consents(self):
        return {}


class CiviCrmParticipantPreeclampsiaDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_preeclampsia_33'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('preeclampsia_id_125', String(255), nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {}

    def consents(self):
        return {}


class CiviCrmParticipantScadDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_scad_15'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('scad_id_58', String(255), nullable=True)
    consent_read_information: Mapped[bool] = mapped_column('consent_read_information_59', Boolean, nullable=True)
    consent_understands_withdrawal: Mapped[bool] = mapped_column('consent_understands_withdrawal_60', Boolean, nullable=True)
    consent_provide_medical_informat: Mapped[bool] = mapped_column('consent_provide_medical_informat_61', Boolean, nullable=True)
    consent_contact_by_research_team: Mapped[bool] = mapped_column('consent_contact_by_research_team_62', Boolean, nullable=True)
    consent_sample_storage: Mapped[bool] = mapped_column('consent_sample_storage_63', Boolean, nullable=True)
    consent_no_financial_benefit: Mapped[bool] = mapped_column('consent_no_financial_benefit_64', Boolean, nullable=True)
    consent_contact_gp: Mapped[bool] = mapped_column('consent_contact_gp_65', Boolean, nullable=True)
    consent_dna_sequencing: Mapped[bool] = mapped_column('consent_dna_sequencing_66', Boolean, nullable=True)
    consent_skin_biopsy: Mapped[bool] = mapped_column('consent_skin_biopsy_67', Boolean, nullable=True)
    consent_understands_how_to_conta: Mapped[bool] = mapped_column('consent_understands_how_to_conta_68', Boolean, nullable=True)
    consent_share_information_with_m: Mapped[bool] = mapped_column('consent_share_information_with_m_69', Boolean, nullable=True)
    consent_access_to_medical_record: Mapped[bool] = mapped_column('consent_access_to_medical_record_70', Boolean, nullable=True)
    consent_contact_for_related_stud: Mapped[bool] = mapped_column('consent_contact_for_related_stud_71', Boolean, nullable=True)
    consent_receive_research_sumary: Mapped[bool] = mapped_column('consent_receive_research_sumary_72', Boolean, nullable=True)
    consent_date: Mapped[datetime] = mapped_column('consent_date_73', DateTime, nullable=True)
    briccs_id: Mapped[str] = mapped_column('briccs_id_88', String(255), nullable=True)
    survey_reference: Mapped[str] = mapped_column('survey_reference_89', String(255), nullable=True)
    scad_visit_id: Mapped[str] = mapped_column('scad_visit_id_90', String(255), nullable=True)
    recruitment_type: Mapped[str] = mapped_column('recruitment_type_91', String(255), nullable=True)
    second_scad_survey_id: Mapped[str] = mapped_column('2nd_scad_survey_id_105', String(255), nullable=True)
    scad_registry_id: Mapped[str] = mapped_column('scad_registry_id_120', String(255), nullable=True)
    family_id: Mapped[str] = mapped_column('family_id_122', String(255), nullable=True)

    def identifiers(self):
        return {
            'Study Identifier': self.study_identifier,
            'BRICCS ID': self.briccs_id,
            'Survey Reference': self.survey_reference,
            'Survey 2nd Reference': self.second_scad_survey_id,
            'Visit ID': self.scad_visit_id,
            'Registry ID': self.scad_registry_id,
            'Family ID': self.family_id,
        }

    def other(self):
        return {'Recruitment Type': self.recruitment_type}

    def consents(self):
        return {
            'Read Information': self.consent_read_information,
            'Understands Withdrawal': self.consent_understands_withdrawal,
            'Provide Medical Information': self.consent_provide_medical_informat,
            'Contact by Research Team': self.consent_contact_by_research_team,
            'Sample Storage': self.consent_sample_storage,
            'No Financial Benefit': self.consent_no_financial_benefit,
            'Contact GP': self.consent_contact_gp,
            'DNA Sequencing': self.consent_dna_sequencing,
            'Skin Biopsy': self.consent_skin_biopsy,
            'Understands How to Contact Study Team': self.consent_understands_how_to_conta,
            'Share Information with M': self.consent_share_information_with_m,
            'Access Medical Record': self.consent_access_to_medical_record,
            'Contact for Related Studies': self.consent_contact_for_related_stud,
            'Receive Research Summary': self.consent_receive_research_sumary,
            'Consent Date': self.consent_date,
        }


class CiviCrmParticipantScadRegisterDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_scad_register_37'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('scad_registry_id_131', String(255), nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {}

    def consents(self):
        return {}


class CiviCrmParticipantSpiralDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_spiral_32'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('spiral_id_124', String(255), nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {}

    def consents(self):
        return {}


class CiviCrmParticipantTmaoDetails(CiviCrmParticipantDetails):
    __tablename__ = 'civicrm_value_tmao_18'
    __bind_key__ = 'civicrm'
    __mapper_args__ = {
        "concrete": True,
    }

    study_identifier: Mapped[str] = mapped_column('tmao_id_79', String(255), nullable=True)
    tmao_consent_has_read_informatio: Mapped[bool] = mapped_column('tmao_consent_has_read_informatio_80', Boolean, nullable=True)
    tmao_consent_understands_withdra: Mapped[bool] = mapped_column('tmao_consent_understands_withdra_81', Boolean, nullable=True)
    tmao_consent_permission_to_acces: Mapped[bool] = mapped_column('tmao_consent_permission_to_acces_82', Boolean, nullable=True)
    tmao_consent_gp_informed: Mapped[bool] = mapped_column('tmao_consent_gp_informed_83', Boolean, nullable=True)
    tmao_consent_to_enrol: Mapped[bool] = mapped_column('tmao_consent_to_enrol_84', Boolean, nullable=True)
    tmao_consent_to_store_blood: Mapped[bool] = mapped_column('tmao_consent_to_store_blood_85', Boolean, nullable=True)

    def identifiers(self):
        return {'Study Identifier': self.study_identifier}

    def other(self):
        return {}

    def consents(self):
        return {
            'Read Information': self.tmao_consent_has_read_informatio,
            'Understand Withdrawal': self.tmao_consent_understands_withdra,
            'Permission to Access': self.tmao_consent_permission_to_acces,
            'Inform GP': self.tmao_consent_gp_informed,
            'Enrolment': self.tmao_consent_to_enrol,
            'Store Blood': self.tmao_consent_to_store_blood,
        }


class CiviCrmContact(db.Model):
    __tablename__ = 'civicrm_contact'
    __bind_key__ = 'civicrm'

    id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True)
    contact_type: Mapped[str] = mapped_column(String(64), nullable=True)
    contact_sub_type: Mapped[str] = mapped_column(String(255), nullable=True)
    do_not_email: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    do_not_phone: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    do_not_mail: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    do_not_sms: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    do_not_trade: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_opt_out: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    legal_identifier: Mapped[str] = mapped_column(String(32), nullable=True)
    external_identifier: Mapped[str] = mapped_column(String(64), nullable=False, server_default='0')
    sort_name: Mapped[str] = mapped_column(String(128), nullable=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=True)
    nick_name: Mapped[str] = mapped_column(String(128), nullable=True)
    legal_name: Mapped[str] = mapped_column(String(128), nullable=True)
    image_URL: Mapped[str] = mapped_column(String(4000), nullable=True)
    preferred_communication_method: Mapped[str] = mapped_column(String(255), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(5), nullable=True)
    preferred_mail_format: Mapped[str] = mapped_column(String(8), nullable=True)
    hash: Mapped[str] = mapped_column(String(32), nullable=True)
    api_key: Mapped[str] = mapped_column(String(32), nullable=True)
    source: Mapped[str] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=True)
    middle_name: Mapped[str] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str] = mapped_column(String(64), nullable=True)
    prefix_id: Mapped[int] = mapped_column(Integer, nullable=True)
    suffix_id: Mapped[int] = mapped_column(Integer, nullable=True)
    formal_title: Mapped[str] = mapped_column(String(64), nullable=True)
    communication_style_id: Mapped[int] = mapped_column(Integer, nullable=True)
    email_greeting_id: Mapped[int] = mapped_column(Integer, nullable=True)
    email_greeting_custom: Mapped[str] = mapped_column(String(128), nullable=True)
    email_greeting_display: Mapped[str] = mapped_column(String(255), nullable=True)
    postal_greeting_id: Mapped[int] = mapped_column(Integer, nullable=True)
    postal_greeting_custom: Mapped[str] = mapped_column(String(128), nullable=True)
    postal_greeting_display: Mapped[str] = mapped_column(String(255), nullable=True)
    addressee_id: Mapped[int] = mapped_column(Integer, nullable=True)
    addressee_custom: Mapped[str] = mapped_column(String(128), nullable=True)
    addressee_display: Mapped[str] = mapped_column(String(255), nullable=True)
    job_title: Mapped[str] = mapped_column(String(255), nullable=True)
    gender_id: Mapped[int] = mapped_column(Integer, nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=True)
    is_deceased: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deceased_date: Mapped[date] = mapped_column(Date, nullable=True)
    household_name: Mapped[str] = mapped_column(String(128), nullable=True)
    primary_contact_id: Mapped[int] = mapped_column(Integer, nullable=True)
    organization_name: Mapped[str] = mapped_column(String(128), nullable=True)
    sic_code: Mapped[str] = mapped_column(String(8), nullable=True)
    user_unique_id: Mapped[str] = mapped_column(String(255), nullable=True)
    employer_id: Mapped[int] = mapped_column(Integer, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_date: Mapped[date] = mapped_column(Date, nullable=True)
    modified_date: Mapped[date] = mapped_column(Date, nullable=True)

    gender: Mapped[CiviCrmGender] = relationship(
        CiviCrmGender,
        foreign_keys=[gender_id],
        primaryjoin='CiviCrmGender.value == CiviCrmContact.gender_id',
    )

    contact_ids: Mapped[CiviCrmContactIds] = relationship(
        CiviCrmContactIds,
        foreign_keys=[id],
        primaryjoin='CiviCrmContactIds.entity_id == CiviCrmContact.id',
    )

    @property
    def full_name(self):
        return ' '.join([self.first_name, self.last_name])


class CiviCrmParticipant(db.Model):
    __tablename__ = 'civicrm_case'
    __bind_key__ = 'civicrm'

    id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True)
    study_id: Mapped[int] = mapped_column('case_type_id', Integer, nullable=False)
    subject: Mapped[str] = mapped_column(String(128), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status_id: Mapped[int] = mapped_column(Integer, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False)

    study: Mapped[CiviCrmStudy] = relationship(
        CiviCrmStudy,
        foreign_keys=[study_id],
        primaryjoin='CiviCrmStudy.id == CiviCrmParticipant.study_id',
        backref=backref("participants", cascade="delete, delete-orphan")
    )

    status: Mapped[CiviCrmCaseStatus] = relationship(
        CiviCrmCaseStatus,
        foreign_keys=[status_id],
        primaryjoin='CiviCrmCaseStatus.value == CiviCrmParticipant.status_id',
    )

    @property
    def identifiers(self):
        result = {}
        
        for d in self.details:
            for k, v in d.identifiers().items():
                result[k] = v

        return result


    @property
    def other_details(self):
        result = {}
        
        for d in self.details:
            for k, v in d.other().items():
                result[k] = v

        return result

    @property
    def consents(self):
        result = {}
        
        for d in self.details:
            for k, v in d.consents().items():
                result[k] = v

        return result

    @property
    @cached(cache=TTLCache(maxsize=1024, ttl=60*60))
    def details(self):
        result = []

        # OK.  So, this next bit of code is a bit crazy, but that's because I think
        # there is a bug in SqlAlchemy where concrete table inheritance doesn't
        # work with bind_keys (that is, tables in other databases).  Therefore,
        # instead of using relationships to access the associated data, I'm having
        # to query each subclass table separately.  Good fun!

        for cls in [
            CiviCrmParticipantAmazeDetails,
            CiviCrmParticipantBioresourceSubStudyDetails,
            CiviCrmParticipantBraveDetails,
            CiviCrmParticipantBriccsDetails,
            CiviCrmParticipantCardiometDetails,
            CiviCrmParticipantDiscordanceDetails,
            CiviCrmParticipantDreamDetails,
            CiviCrmParticipantEmmace4Details,
            CiviCrmParticipantFastDetails,
            CiviCrmParticipantFoamiDetails,
            CiviCrmParticipantGenvascInvoiceDetails,
            CiviCrmParticipantGenvascDetails,
            CiviCrmParticipantGenvascWithdrawalDetails,
            CiviCrmParticipantGlobalLeadersDetails,
            CiviCrmParticipantGraphic2Details,
            CiviCrmParticipantIndapamideDetails,
            CiviCrmParticipantIntervalDetails,
            CiviCrmParticipantLentenDetails,
            CiviCrmParticipantLimbDetails,
            CiviCrmParticipantNationalBioresourceDetails,
            CiviCrmParticipantBioresourceDetails,
            CiviCrmParticipantBioresourceWithdrawalDetails,
            CiviCrmParticipantOmicsDetails,
            CiviCrmParticipantPredictDetails,
            CiviCrmParticipantPreeclampsiaDetails,
            CiviCrmParticipantScadDetails,
            CiviCrmParticipantScadRegisterDetails,
            CiviCrmParticipantSpiralDetails,
            CiviCrmParticipantTmaoDetails,
        ]:
            result.extend(
                db.session.execute(select(cls).where(cls.entity_id == self.id)).scalars()
            )
        
        return result
    
    @property
    def contact(self):
        if self.participant_contacts:
            return self.participant_contacts[0].contact


class CiviCrmParticipantContact(db.Model):
    __tablename__ = 'civicrm_case_contact'
    __bind_key__ = 'civicrm'

    id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True)
    participant_id: Mapped[int] = mapped_column('case_id', Integer, nullable=False)
    contact_id: Mapped[int] = mapped_column(Integer, nullable=False)

    participant: Mapped[CiviCrmParticipant] = relationship(
        CiviCrmParticipant,
        foreign_keys=[participant_id],
        primaryjoin='CiviCrmParticipantContact.participant_id == CiviCrmParticipant.id',
        backref=backref("participant_contacts", cascade="delete, delete-orphan")
    )

    contact: Mapped[CiviCrmParticipant] = relationship(
        CiviCrmContact,
        foreign_keys=[contact_id],
        primaryjoin='CiviCrmParticipantContact.contact_id == CiviCrmContact.id',
        backref=backref("participant_contacts", cascade="delete, delete-orphan")
    )
