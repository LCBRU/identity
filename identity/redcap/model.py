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
            for type, field in self._get_identifier_type_fields().items()
            if (participant_details[field] or '').strip()
        ]
    
    # Abstract Methods

    def _fill_ecrf_details(self, record, ecrf):
        pass

    def _get_identifier_type_fields(self):
        return {}

    def _get_fields(self):
        return []

    def __str__(self):
        return self.type


class BriccsParticipantImportStrategy(ParticipantImportStrategy):
    __mapper_args__ = {
        "polymorphic_identity": 'Briccs Participant Import Strategy',
    }

    def _get_fields(self):
        return [
            'int_date',
            'nhs_number',
            's_number',
            'first_name',
            'last_name',
            'gender',
            'address_postcode',
            'dob',
            'study_status_comp_yn',
            'non_complete_rsn',
            'wthdrw_date',
            'wthdrwl_optn_chsn',
        ]
    
    def _fill_ecrf_details(self, record, ecrf):
        ecrf.recruitment_date=parse(record['int_date']) if record['int_date'] else None
        ecrf.first_name=record['first_name']
        ecrf.last_name=record['last_name']
        ecrf.sex=record['gender']
        ecrf.postcode=record['address_postcode']
        ecrf.birth_date=parse(record['dob']) if record['dob'] else None
        ecrf.complete_or_expected=(record['study_status_comp_yn'] != '0')
        ecrf.non_completion_reason=record['non_complete_rsn']
        ecrf.withdrawal_date=parse(record['wthdrw_date']) if record['wthdrw_date'] else None
        ecrf.post_withdrawal_keep_samples=(record['wthdrwl_optn_chsn'] in ['0', '1'])
        ecrf.post_withdrawal_keep_data=(record['wthdrwl_optn_chsn'] in ['0', '2'])
        ecrf.brc_opt_out=(record['wthdrwl_optn_chsn'] == '4')

        return ecrf

    def _get_identifier_type_fields(self):
        return {
            ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__: 'record',
            ParticipantIdentifierType.__BRICCS_ID__: 'record',
            ParticipantIdentifierType.__NHS_NUMBER__: 'nhs_number',
            ParticipantIdentifierType.__UHL_SYSTEM_NUMBER__: 's_number',
        }


class PilotParticipantImportStrategy(ParticipantImportStrategy):
    __mapper_args__ = {
        "polymorphic_identity": 'Pilot Participant Import Strategy',
    }

    def _get_fields(self):
        return [
            'date_time_of_admission',
            'sex',
        ]
    
    def _fill_ecrf_details(self, record, ecrf):
        ecrf.recruitment_date=parse(record['date_time_of_admission']) if record['date_time_of_admission'] else None
        ecrf.sex=record['sex']

        return ecrf

    def _get_identifier_type_fields(self):
        return {
            ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__: 'record',
            ParticipantIdentifierType.__PILOT_ID__: 'record',
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
    post_withdrawal_keep_samples = db.Column(db.Boolean)
    post_withdrawal_keep_data = db.Column(db.Boolean)
    brc_opt_out = db.Column(db.Boolean)
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
