from identity.services.validators import parse_date_or_none
from flask import current_app
from identity.model.id import ParticipantIdentifierSource
from identity.database import db
from datetime import datetime
from identity.database import db
from identity.model import Study
from identity.model.security import User


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


class ParticipantImportDefinition(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    study_id = db.Column(db.Integer, db.ForeignKey(Study.id))
    study = db.relationship(Study)

    redcap_project_id = db.Column(db.Integer, db.ForeignKey(RedcapProject.id))
    redcap_project = db.relationship(RedcapProject)

    recruitment_date_column_name = db.Column(db.String(100))
    first_name_column_name = db.Column(db.String(100))
    last_name_column_name = db.Column(db.String(100))
    postcode_column_name = db.Column(db.String(100))
    birth_date_column_name = db.Column(db.String(100))
    withdrawal_date_column_name = db.Column(db.String(100))

    withdrawn_from_study_column_name = db.Column(db.String(100))
    withdrawn_from_study_values = db.Column(db.String(500))

    sex_column_name = db.Column(db.String(100))
    sex_column_map = db.Column(db.String(500))

    complete_or_expected_column_name = db.Column(db.String(100))
    complete_or_expected_values = db.Column(db.String(500))

    post_withdrawal_keep_samples_column_name = db.Column(db.String(100))
    post_withdrawal_keep_samples_values = db.Column(db.String(500))

    post_withdrawal_keep_data_column_name = db.Column(db.String(100))
    post_withdrawal_keep_data_values = db.Column(db.String(500))

    brc_opt_out_column_name = db.Column(db.String(100))
    brc_opt_out_values = db.Column(db.String(500))

    excluded_from_analysis_column_name = db.Column(db.String(100))
    excluded_from_analysis_values = db.Column(db.String(500))

    excluded_from_study_column_name = db.Column(db.String(100))
    excluded_from_study_values = db.Column(db.String(500))

    identities_map = db.Column(db.String(500))

    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    def _parse_list_string(self, value):
        if value is None or len(value.strip()) == 0:
            return []
        else:
            return [i.strip() for i in value.split(',')]

    def _parse_dictionary_string(self, value):
        return {k: v for k, v in [i.split(':') for i in self._parse_list_string(value)]}

    @property
    def withdrawn_from_study_value_array(self):
        return self._parse_list_string(self.withdrawn_from_study_values)

    @property
    def complete_or_expected_value_array(self):
        return self._parse_list_string(self.complete_or_expected_values)

    @property
    def post_withdrawal_keep_samples_value_array(self):
        return self._parse_list_string(self.post_withdrawal_keep_samples_values)

    @property
    def post_withdrawal_keep_data_value_array(self):
        return self._parse_list_string(self.post_withdrawal_keep_data_values)

    @property
    def brc_opt_out_value_array(self):
        return self._parse_list_string(self.brc_opt_out_values)

    @property
    def excluded_from_analysis_value_array(self):
        return self._parse_list_string(self.excluded_from_analysis_values)

    @property
    def excluded_from_study_value_array(self):
        return self._parse_list_string(self.excluded_from_study_values)

    @property
    def sex_column_map_dictionary(self):
        return self._parse_dictionary_string(self.sex_column_map)

    @property
    def identities_map_dictionary(self):
        return self._parse_dictionary_string(self.identities_map)

    def _get_fields(self):
        return filter(None, set([
            self.recruitment_date_column_name,
            self.first_name_column_name,
            self.last_name_column_name,
            self.postcode_column_name,
            self.birth_date_column_name,
            self.withdrawal_date_column_name,
            self.withdrawn_from_study_column_name,
            self.sex_column_name,
            self.complete_or_expected_column_name,
            self.post_withdrawal_keep_samples_column_name,
            self.post_withdrawal_keep_data_column_name,
            self.brc_opt_out_column_name,
            self.excluded_from_analysis_column_name,
            self.excluded_from_study_column_name,
            *self.identities_map_dictionary.values(),
        ]))

    def get_query(self):
        group_concat_cols = ", ".join(f"GROUP_CONCAT(DISTINCT CASE WHEN field_name = '{f}' THEN VALUE ELSE NULL END) AS {f}" for f in self._get_fields())

        if len(group_concat_cols) > 0:
            group_concat_cols + ','

        ins = ", ".join((f"'{f}'" for f in self._get_fields()))

        if len(ins) > 0:
            ins = f'AND rd.field_name IN ({ins})'

        return f"""
            SELECT
                rd.project_id,
                rd.record,
                {group_concat_cols}
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
                {ins}
            GROUP BY rd.record, rd.project_id
        """

    def fill_ecrf(self, redcap_project, participant_details, existing_ecrf):

        if existing_ecrf is None:
            current_app.logger.info(f'Creating ecrf for participant "{participant_details["record"]}"')
            result = EcrfDetail(
                redcap_project_id=redcap_project.id,
                ecrf_participant_identifier=participant_details['record'],
            )
            result.identifier_source = EcrfParticipantIdentifierSource(study_id=self.study_id)
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
            for type, field in self.identities_map_dictionary.items()
            if (participant_details[field] or '').strip()
        ]

    def _fill_ecrf_details(self, record, ecrf):
        erec = EcrfRecord(record)

        ecrf.recruitment_date = erec.get_parsed_date(self.recruitment_date_column_name)
        ecrf.first_name = erec.get(self.first_name_column_name)
        ecrf.last_name = erec.get(self.last_name_column_name)
        ecrf.postcode = erec.get(self.postcode_column_name)
        ecrf.birth_date = erec.get_parsed_date(self.birth_date_column_name)
        ecrf.sex = self.sex_column_map_dictionary.get(erec.get(self.sex_column_name))
        ecrf.complete_or_expected = erec.get_from_value_array(self.complete_or_expected_column_name, self.complete_or_expected_value_array)
        ecrf.withdrawal_date = erec.get_parsed_date(self.withdrawal_date_column_name)
        ecrf.withdrawn_from_study = erec.get_from_value_array(self.withdrawn_from_study_column_name, self.withdrawn_from_study_value_array)
        ecrf.post_withdrawal_keep_samples = erec.get_from_value_array(self.post_withdrawal_keep_samples_column_name, self.post_withdrawal_keep_samples_value_array)
        ecrf.post_withdrawal_keep_data = erec.get_from_value_array(self.post_withdrawal_keep_data_column_name, self.post_withdrawal_keep_data_value_array)
        ecrf.brc_opt_out = erec.get_from_value_array(self.brc_opt_out_column_name, self.brc_opt_out_value_array)
        ecrf.excluded_from_analysis = erec.get_from_value_array(self.excluded_from_analysis_column_name, self.excluded_from_analysis_value_array)
        ecrf.excluded_from_study = erec.get_from_value_array(self.excluded_from_study_column_name, self.excluded_from_study_value_array)

        return ecrf


class EcrfRecord():
    def __init__(self, record):
        self.record = record
    
    def get(self, column_name):
        if len((column_name or '').strip()) == 0 or column_name not in self.record:
            return None
        else:
            return self.record[column_name].strip()

    def get_parsed_date(self, column_name):
        return parse_date_or_none(self.get(self.column_name))

    def get_from_value_array(self, column_name, value_array):
        if len(value_array or []) == 0:
            return None
        if len((column_name or '').strip()) == 0 or column_name not in self.record:
            return None

        value = self.get(column_name)

        if value is None and '<isnull>' in value_array:
            return True
        if value is not None and '<isnotnull>' in value_array:
            return True

        return value in value_array


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
