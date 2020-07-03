import urllib.parse
from dateutil.parser import parse
from flask import current_app
from identity.model.id import (
    ParticipantIdentifier,
    ParticipantIdentifierType,
)
from identity.database import db
from datetime import datetime
from identity.database import db
from identity.model import Study
from identity.model.id import ParticipantIdentifierSource, ParticipantIdentifier
from identity.model.security import User


class ParticipantImportStrategy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "ParticipantImportStrategy",
        "polymorphic_on": type,
    }

    def _get_fields(self):
        return filter(None, set([
            self.recruitment_date_column_name,
            self.first_name_column_name,
            self.last_name_column_name,
            self.sex_column_name,
            self.post_code_column_name,
            self.birth_date_column_name,
            self.complete_or_expected_column_name,
            self.non_completion_reason_column_name,
            self.withdrawal_date_column_name,
            self.post_withdrawal_keep_samples_column_name,
            self.post_withdrawal_keep_data_column_name,
            self.brc_opt_out_column_name,
            *self.identity_map.values(),
        ]))

    def get_query(self):
        group_concats = ", ".join(f"GROUP_CONCAT(DISTINCT CASE WHEN field_name = '{f}' THEN VALUE ELSE NULL END) AS {f}" for f in self._get_fields())
        ins = ", ".join((f"'{f}'" for f in self._get_fields()))

        return f"""
            SELECT
                rd.project_id,
                rd.record,
                {group_concats},
                rl.last_update_timestamp AS last_update_timestamp
            FROM redcap_data rd
            JOIN (
                SELECT
                    pk,
                    project_id,
                    MAX(COALESCE(ts, 0)) AS last_update_timestamp
                FROM redcap_log_event
                WHERE event NOT IN ('DATA_EXPORT', 'DELETE')
                    # Ignore events caused by the data import from
                    # the mobile app
                    AND page NOT IN ('DataImportController:index')
                    AND project_id = :project_id
                    AND object_type = 'redcap_data'
                    AND ts > :timestamp
                GROUP BY pk, project_id
            ) rl ON rl.project_id = rd.project_id
                AND rl.pk = rd.record
            WHERE rd.project_id = :project_id
                AND LENGTH(RTRIM(LTRIM(COALESCE(rd.record, '')))) > 0
                AND rd.field_name IN ({ins})
            GROUP BY rd.record, rd.project_id
        """

    def fill_ecrf(self, redcap_project, participant_details, existing_ecrf):

        if existing_ecrf is None:
            current_app.logger.info(f'Creating ecrf for participant "{participant_details["record"]}"')
            result = EcrfDetail(
                redcap_project_id=redcap_project.id,
                ecrf_participant_identifier=participant_details['record'],
            )
            result.identifier_source = EcrfParticipantIdentifierSource(study_id=redcap_project.study_id)
        else:
            current_app.logger.info(f'Updating ecrf for participant: {participant_details["record"]}')
            result = existing_ecrf

        return self._fill_ecrf_details(participant_details, result)

    def extract_identifiers(self, participant_details):
        return [
            {
                'type': type,
                'identifier': participant_details[field].strip(),
            }
            for type, field in self.identity_map.items()
            if (participant_details[field] or '').strip()
        ]
    
    def _fill_ecrf_details(self, record, ecrf):

        if self.recruitment_date_column_name is not None and record[self.recruitment_date_column_name]:
            ecrf.recruitment_date=parse(record[self.recruitment_date_column_name])
        else:
            ecrf.recruitment_date = None

        if self.first_name_column_name is not None:
            ecrf.first_name=record[self.first_name_column_name]
        else:
            ecrf.first_name = None

        if self.last_name_column_name is not None:
            ecrf.last_name=record[self.last_name_column_name]
        else:
            ecrf.last_name = None

        if self.sex_column_name is not None and self.sex_column_map is not None and record[self.sex_column_name] in self.sex_column_map:
            ecrf.sex=self.sex_column_map[record[self.sex_column_name]]
        else:
            ecrf.sex = None

        if self.post_code_column_name is not None:
            ecrf.postcode=record[self.post_code_column_name]
        else:
            ecrf.postcode = None
        
        if self.birth_date_column_name is not None and record[self.birth_date_column_name]:
            ecrf.birth_date=parse(record[self.birth_date_column_name])
        else:
            ecrf.birth_date = None

        if self.complete_or_expected_column_name is not None:
            ecrf.complete_or_expected = (record[self.complete_or_expected_column_name] in self.complete_or_expected_values)
        else:
            ecrf.complete_or_expected = None

        if self.non_completion_reason_column_name is not None:
            ecrf.non_completion_reason = record[self.non_completion_reason_column_name]
        else:
            ecrf.non_completion_reason = None

        if self.withdrawal_date_column_name is not None and record[self.withdrawal_date_column_name]:
            ecrf.withdrawal_date=parse(record[self.withdrawal_date_column_name])
        else:
            ecrf.withdrawal_date = None

        if self.withdrawn_from_study_if_not_empty_column_name is not None:
            if record[self.withdrawal_date_column_name]:
                ecrf.withdrawn_from_study = True
            else:
                ecrf.withdrawn_from_study = False
        elif self.withdrawn_from_study_column_name is not None:
            ecrf.withdrawn_from_study=(record[self.withdrawn_from_study_column_name] in self.withdrawn_from_study_values)
        else:
            ecrf.withdrawn_from_study = None

        if self.post_withdrawal_keep_samples_column_name is not None:
            ecrf.post_withdrawal_keep_samples=(record[self.post_withdrawal_keep_samples_column_name] in self.post_withdrawal_keep_samples_values)
        else:
            ecrf.post_withdrawal_keep_samples = None

        if self.post_withdrawal_keep_data_column_name is not None:
            ecrf.post_withdrawal_keep_data=(record[self.post_withdrawal_keep_data_column_name] in self.post_withdrawal_keep_data_values)
        else:
            ecrf.post_withdrawal_keep_data = None

        if self.brc_opt_out_column_name is not None:
            ecrf.brc_opt_out=(record[self.brc_opt_out_column_name] in self.brc_opt_out_values)
        else:
            ecrf.brc_opt_out = None

        if self.excluded_from_analysis_column_name is not None:
            ecrf.excluded_from_analysis=(record[self.excluded_from_analysis_column_name] in self.excluded_from_analysis_values)
        else:
            ecrf.excluded_from_analysis = None

        if self.excluded_from_study_column_name is not None:
            ecrf.excluded_from_study=(record[self.excluded_from_study_column_name] in self.excluded_from_study_values)
        else:
            ecrf.excluded_from_study = None

        return ecrf

    # Abstract Methods

    @property
    def recruitment_date_column_name(self):
        return None
    
    @property
    def first_name_column_name(self):
        return None
    
    @property
    def last_name_column_name(self):
        return None
    
    @property
    def sex_column_name(self):
        return None
    
    @property
    def sex_column_map(self):
        return None
    
    @property
    def post_code_column_name(self):
        return None
    
    @property
    def birth_date_column_name(self):
        return None

    @property
    def complete_or_expected_column_name(self):
        return None
    
    @property
    def complete_or_expected_values(self):
        return []
    
    @property
    def non_completion_reason_column_name(self):
        return None

    @property
    def withdrawal_date_column_name(self):
        return None
    
    @property
    def withdrawn_from_study_column_name(self):
        return None
    
    @property
    def withdrawn_from_study_values(self):
        return []
    
    @property
    def withdrawn_from_study_if_not_empty_column_name(self):
        return None
    
    @property
    def post_withdrawal_keep_samples_column_name(self):
        return None
    
    @property
    def post_withdrawal_keep_samples_values(self):
        return []

    @property
    def post_withdrawal_keep_data_column_name(self):
        return None
    
    @property
    def post_withdrawal_keep_data_values(self):
        return []
    
    @property
    def brc_opt_out_column_name(self):
        return None
    
    @property
    def brc_opt_out_values(self):
        return []
    
    @property
    def excluded_from_analysis_column_name(self):
        return None
    
    @property
    def excluded_from_analysis_values(self):
        return []
    
    @property
    def excluded_from_study_column_name(self):
        return None
    
    @property
    def excluded_from_study_values(self):
        return []
    
    @property
    def identity_map(self):
        return {}

    def __str__(self):
        return self.type


class BriccsParticipantImportStrategy(ParticipantImportStrategy):
    __mapper_args__ = {
        "polymorphic_identity": 'Briccs Participant Import Strategy',
    }

    @property
    def recruitment_date_column_name(self):
        return 'int_date'
    
    @property
    def first_name_column_name(self):
        return 'first_name'
    
    @property
    def last_name_column_name(self):
        return 'last_name'
    
    @property
    def sex_column_name(self):
        return 'gender'
    
    @property
    def sex_column_map(self):
        return {
            '0': 'F',
            '1': 'M',
        }
    
    @property
    def post_code_column_name(self):
        return 'address_postcode'
    
    @property
    def birth_date_column_name(self):
        return 'dob'

    @property
    def complete_or_expected_column_name(self):
        return 'study_status_comp_yn'
    
    @property
    def complete_or_expected_values(self):
        return [None, '1']
    
    @property
    def non_completion_reason_column_name(self):
        return 'non_complete_rsn'

    @property
    def withdrawal_date_column_name(self):
        return 'wthdrw_date'
    
    @property
    def withdrawn_from_study_if_not_empty_column_name(self):
        return 'wthdrw_date'
    
    @property
    def post_withdrawal_keep_samples_column_name(self):
        return 'wthdrwl_optn_chsn'
    
    @property
    def post_withdrawal_keep_samples_values(self):
        return ['0', '1']

    @property
    def post_withdrawal_keep_data_column_name(self):
        return 'wthdrwl_optn_chsn'
    
    @property
    def post_withdrawal_keep_data_values(self):
        return ['0', '2']
    
    @property
    def brc_opt_out_column_name(self):
        return 'wthdrwl_optn_chsn'
    
    @property
    def brc_opt_out_values(self):
        return ['4']
    
    @property
    def identity_map(self):
        return {
            ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__: 'record',
            ParticipantIdentifierType.__BRICCS_ID__: 'record',
            ParticipantIdentifierType.__NHS_NUMBER__: 'nhs_number',
            ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 's_number',
        }


class CvlpritParticipantImportStrategy(ParticipantImportStrategy):
    __mapper_args__ = {
        "polymorphic_identity": 'Cvlprit Participant Import Strategy',
    }

    @property
    def sex_column_name(self):
        return 'sex'
    
    @property
    def sex_column_map(self):
        return {
            '1': 'M',
            '2': 'F',
        }
    
    @property
    def identity_map(self):
        return {
            ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__: 'patient_id',
            ParticipantIdentifierType.__CVLPRIT_ID__: 'patient_id',
            ParticipantIdentifierType.__CVLPRIT_LOCAL_ID__: 'local_id',
        }


class PilotParticipantImportStrategy(ParticipantImportStrategy):
    __mapper_args__ = {
        "polymorphic_identity": 'Pilot Participant Import Strategy',
    }

    @property
    def recruitment_date_column_name(self):
        return 'date_time_of_admission'
    
    @property
    def sex_column_name(self):
        return 'sex'
    
    @property
    def sex_column_map(self):
        return {
            '0': 'M',
            '1': 'F',
        }
    
    @property
    def identity_map(self):
        return {
            ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__: 'record',
            ParticipantIdentifierType.__PILOT_ID__: 'record',
        }


class DreamParticipantImportStrategy(ParticipantImportStrategy):
    __mapper_args__ = {
        "polymorphic_identity": 'Dream Participant Import Strategy',
    }

    @property
    def recruitment_date_column_name(self):
        return 'date_enrolled'

    @property
    def sex_column_name(self):
        return 'sex'

    @property
    def sex_column_map(self):
        return {
            '1': 'M',
            '2': 'F',
            '3': 'T',
            '4': 'O',
        }
    
    @property
    def withdrawn_from_study_column_name(self):
        return 'reason_for_participant_rem'

    @property
    def withdrawn_from_study_values(self):
        return ['6']

    @property
    def excluded_from_analysis_column_name(self):
        return 'inc_in_eos_analysis'

    @property
    def excluded_from_analysis_values(self):
        return [None, '0']

    @property
    def identity_map(self):
        return {
            ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__: 'record',
            ParticipantIdentifierType.__DREAM_ID__: 'record',
        }


class BioresourceLegacyParticipantImportStrategy(ParticipantImportStrategy):
    __mapper_args__ = {
        "polymorphic_identity": 'Bioresource Legacy Participant Import Strategy',
    }

    @property
    def recruitment_date_column_name(self):
        return 'date_of_sig'
    
    @property
    def sex_column_name(self):
        return 'gender'
    
    @property
    def sex_column_map(self):
        return {
            '1': 'M',
            '2': 'F',
            '0': 'N',
        }
    
    @property
    def birth_date_column_name(self):
        return 'date_of_birth'

    @property
    def complete_or_expected_column_name(self):
        return 'study_status_comp_yn'
    
    @property
    def complete_or_expected_values(self):
        return [None, '1']
    
    @property
    def non_completion_reason_column_name(self):
        return 'non_complete_rsn'

    @property
    def withdrawal_date_column_name(self):
        return 'wthdrw_date'
    
    @property
    def withdrawn_from_study_if_not_empty_column_name(self):
        return 'wthdrw_date'
    
    @property
    def post_withdrawal_keep_samples_column_name(self):
        return 'wthdrwl_optn_chsn'
    
    @property
    def post_withdrawal_keep_samples_values(self):
        return ['0', '1']

    @property
    def post_withdrawal_keep_data_column_name(self):
        return 'wthdrwl_optn_chsn'
    
    @property
    def post_withdrawal_keep_data_values(self):
        return ['0', '2']
    
    @property
    def brc_opt_out_column_name(self):
        return 'wthdrwl_optn_chsn'
    
    @property
    def brc_opt_out_values(self):
        return ['4']
    
    @property
    def identity_map(self):
        return {
            ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__: 'record',
            ParticipantIdentifierType.__BIORESOURCE_ID__: 'record',
        }


class Graphic2ParticipantImportStrategy(ParticipantImportStrategy):
    __mapper_args__ = {
        "polymorphic_identity": 'Graphic2 Participant Import Strategy',
    }

    @property
    def recruitment_date_column_name(self):
        return 'date_interview'
    
    @property
    def sex_column_name(self):
        return 'gender'
    
    @property
    def sex_column_map(self):
        return {
            '0': 'F',
            '1': 'M',
        }
    
    @property
    def birth_date_column_name(self):
        return 'dob'

    @property
    def excluded_from_analysis_column_name(self):
        return 'exclude_from_analysis'
    
    @property
    def excluded_from_analysis_values(self):
        return ['1']
    
    @property
    def identity_map(self):
        return {
            ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__: 'record',
            ParticipantIdentifierType.__GRAPHICS2_ID__: 'record',
        }


class RedcapInstance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    database_name = db.Column(db.String(100), nullable=False)
    base_url = db.Column(db.String(500), nullable=False)
    version = db.Column(db.String(10), nullable=False)
    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    def __str__(self):
        return self.name


class RedcapProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    project_id = db.Column(db.Integer, nullable=False)
    redcap_instance_id = db.Column(db.Integer, db.ForeignKey(RedcapInstance.id), nullable=False)
    redcap_instance = db.relationship(RedcapInstance, backref=db.backref("projects"))
    study_id = db.Column(db.Integer, db.ForeignKey(Study.id))
    study = db.relationship(Study, backref=db.backref("redcap_projects"))
    participant_import_strategy_id =  db.Column(db.Integer, db.ForeignKey(ParticipantImportStrategy.id), nullable=True)
    participant_import_strategy = db.relationship(ParticipantImportStrategy, backref=db.backref("redcap_projects"))
    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    def __repr__(self):
        return f'<Project: "{self.name}" from instance "{self.redcap_instance.name}">'

    def __str__(self):
        return self.name

    def get_link(self, record_id):
        return "/".join(map(lambda x: str(x).rstrip('/'), [
            self.redcap_instance.base_url,
            f'redcap_v{self.redcap_instance.version}/DataEntry/record_home.php?pid={self.project_id}&id={record_id}'],
        ))


class EcrfDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    redcap_project_id = db.Column(db.Integer, db.ForeignKey(RedcapProject.id), nullable=False)
    redcap_project = db.relationship(RedcapProject, backref=db.backref("details"))

    ecrf_participant_identifier = db.Column(db.String(100))
    recruitment_date = db.Column(db.Date)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    sex = db.Column(db.String(1))
    postcode = db.Column(db.String(10))
    birth_date = db.Column(db.Date)
    complete_or_expected = db.Column(db.Boolean)
    non_completion_reason = db.Column(db.String(10))
    withdrawal_date = db.Column(db.Date)
    withdrawn_from_study = db.Column(db.Boolean)
    post_withdrawal_keep_samples = db.Column(db.Boolean)
    post_withdrawal_keep_data = db.Column(db.Boolean)
    brc_opt_out = db.Column(db.Boolean)
    excluded_from_analysis = db.Column(db.Boolean)
    excluded_from_study = db.Column(db.Boolean)
    ecrf_timestamp = db.Column(db.BigInteger)

    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    identifier_source = db.relationship("EcrfParticipantIdentifierSource", back_populates="ecrf_detail", uselist=False)

    def __str__(self):
        return self.ecrf_participant_identifier


class EcrfParticipantIdentifierSource(ParticipantIdentifierSource):
    __tablename__ = 'ecrf_participant_identifier_source'

    participant_identifier_source_id = db.Column(db.Integer, db.ForeignKey('participant_identifier_source.id'), primary_key=True)
    ecrf_detail_id = db.Column(db.Integer, db.ForeignKey(EcrfDetail.id), nullable=False)
    ecrf_detail = db.relationship("EcrfDetail", back_populates="identifier_source")

    __mapper_args__ = {
        'polymorphic_identity':'ecrf_participant_identifier_source',
    }
