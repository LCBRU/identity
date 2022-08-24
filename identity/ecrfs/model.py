from lbrc_flask.security import system_user_id
from lbrc_flask.string_functions import decode_dictionary_string, decode_list_string, encode_dictionary_string, encode_list_string
from identity.setup.civicrm_instances import CiviCrmInstanceDetail
from sqlalchemy import func, select
from memoization import cached
from lbrc_flask.validators import parse_date_or_none
from flask import current_app
from identity.model.id import ParticipantIdentifierSource
from identity.database import redcap_engine
from datetime import datetime
from lbrc_flask.database import db
from identity.model import Study
from identity.model.security import User
from sqlalchemy.orm import column_property
from sqlalchemy.sql import text


class EcrfSource(db.Model):
    __tablename__ = 'ecrf_source'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100))
    last_updated_datetime = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    last_updated_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey(User.id),
        default=system_user_id,
        onupdate=system_user_id,
    )
    last_updated_by_user = db.relationship(User)

    __mapper_args__ = {
        'polymorphic_identity':'ecrf_source',
        'polymorphic_on':type,
    }

    def __str__(self):
        return self.name

    def has_new_data(self, existing_timestamp):
        latest_timesheet = self._get_latest_timestamp()

        if latest_timesheet > existing_timestamp:
            current_app.logger.info(f'{self.name} has new data - existing timestamp: "{existing_timestamp}"; latest Timestamp: "{latest_timesheet}".')
            return True
        else:
            return False

    def get_participants(self, pid):
        raise NotImplementedError()


class EcrfDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    participant_import_definition_id = db.Column(db.Integer, db.ForeignKey('participant_import_definition.id'), nullable=False)
    participant_import_definition = db.relationship('ParticipantImportDefinition', backref=db.backref("ecrfs"))

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

    identifier_source = db.relationship("EcrfParticipantIdentifierSource", cascade="all, delete-orphan", back_populates="ecrf_detail", uselist=False)

    def __str__(self):
        return self.ecrf_participant_identifier


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

    @cached(ttl=30)
    def get_newest_timestamps(self):
        with redcap_engine(self.database_name) as conn:
            return {r['project_id']: r['ts'] for r in conn.execute('''
                SELECT
                    project_id,
                    MAX(COALESCE(ts, 0)) AS ts
                FROM redcap_log_event
                WHERE event IN ('INSERT', 'UPDATE')
                    # Ignore events caused by the data import from
                    # the mobile app
                    AND page NOT IN ('DataImportController:index')
                    AND object_type = 'redcap_data'
                GROUP BY project_id
            ''')}


class RedcapProject(EcrfSource):

    __tablename__ = 'redcap_project'
    __mapper_args__ = {
        'polymorphic_identity':'redcap_project',
    }

    id = db.Column(db.Integer, db.ForeignKey(EcrfSource.id), primary_key=True)
    project_id = db.Column(db.Integer, nullable=False)
    redcap_instance_id = db.Column(db.Integer, db.ForeignKey(RedcapInstance.id), nullable=False)
    redcap_instance = db.relationship(RedcapInstance, backref=db.backref("projects"))
    
    def get_link(self, record_id=None):
        if record_id is None:
            return "/".join(map(lambda x: str(x).rstrip('/'), [
                self.redcap_instance.base_url,
                f'redcap_v{self.redcap_instance.version}//index.php?pid={self.project_id}'],
            ))
        else:
            return "/".join(map(lambda x: str(x).rstrip('/'), [
                self.redcap_instance.base_url,
                f'redcap_v{self.redcap_instance.version}/DataEntry/record_home.php?pid={self.project_id}&id={record_id}'],
            ))

    def _get_latest_timestamp(self):
        return self.redcap_instance.get_newest_timestamps().get(self.project_id, -1)

    def _get_query(self, pid):
        group_concat_cols = ", ".join(
            f"GROUP_CONCAT(DISTINCT CASE WHEN field_name = '{f}' THEN VALUE ELSE NULL END) AS {f}"
            for f in pid.get_fields() if f not in ['record', 'last_update_timestamp', 'project_id']
        )

        if len(group_concat_cols) > 0:
            group_concat_cols += ','

        ins = ", ".join((f"'{f}'" for f in pid.get_fields()))

        if len(ins) > 0:
            ins = f'AND rd.field_name IN ({ins})'

        return f"""
            SELECT
                rl.project_id,
                rl.pk AS record,
                {group_concat_cols}
                rl.last_update_timestamp AS last_update_timestamp
            FROM (
                SELECT
                    pk,
                    project_id,
                    MAX(COALESCE(ts, 0)) AS last_update_timestamp
                FROM redcap_log_event
		        WHERE event IN ('INSERT', 'UPDATE')
                    # Ignore events caused by the data import from
                    # the mobile app
                    AND page NOT IN ('DataImportController:index')
                    AND project_id = :project_id
                    AND object_type = 'redcap_data'
                    AND ts > :timestamp
                    AND LENGTH(RTRIM(LTRIM(COALESCE(pk, '')))) > 0
                GROUP BY pk, project_id
            ) rl
            LEFT JOIN redcap_data rd
				ON rl.project_id = rd.project_id
                AND rl.pk = rd.record
                {ins}
            GROUP BY rl.pk, rl.project_id
        """

    def get_participants(self, pid):
        with redcap_engine(self.redcap_instance.database_name) as conn:
            return conn.execute(
                text(self._get_query(pid)),
                timestamp=pid.latest_timestamp,
                project_id=self.project_id,
            )

    def __repr__(self):
        return f'<Project: "{self.name}" from instance "{self.redcap_instance.name}">'

    def __str__(self):
        return f'REDCap {self.redcap_instance.name}: {self.name}'



class CustomEcrfSource(EcrfSource):

    __tablename__ = 'custom_ecrf_source'
    __mapper_args__ = {
        'polymorphic_identity':'custom',
    }

    id = db.Column(db.Integer, db.ForeignKey(EcrfSource.id), primary_key=True)
    database_name = db.Column(db.String(100), nullable=False)
    data_query = db.Column(db.UnicodeText(), nullable=False)
    most_recent_timestamp_query = db.Column(db.UnicodeText(), nullable=False)
    link = db.Column(db.String(500), nullable=False)
    
    def get_link(self, record_id):
        return self.link.format(record_id=record_id)

    def _get_latest_timestamp(self):
        with redcap_engine(self.database_name) as conn:
            return conn.scalar(text(self.most_recent_timestamp_query))

    def get_participants(self, pid):
        with redcap_engine(self.database_name) as conn:
            return conn.execute(
                text(self.data_query),
                timestamp=pid.latest_timestamp
            )

    def __repr__(self):
        return f'<Custom Ecrf Source: "{self.name}"">'

    def __str__(self):
        return f'Custom {self.name}'


class CiviCrmEcrfSource(EcrfSource):

    __tablename__ = 'civicrm_ecrf_source'
    __mapper_args__ = {
        'polymorphic_identity':'civicrm',
    }

    id = db.Column(db.Integer, db.ForeignKey(EcrfSource.id), primary_key=True)
    case_type_id = db.Column(db.Integer)
    custom_tables = db.Column(db.String(500))

    @staticmethod
    @cached(ttl=30)
    def get_newest_timestamps():
        with redcap_engine(CiviCrmInstanceDetail.UHL_LIVE['database_name']) as conn:
            return {r['case_type_id']: r['ts'] for r in conn.execute(text('''
                SELECT case_type_id, CONVERT(DATE_FORMAT(MAX(latest_datetime), '%Y%m%d%H%i%S'), UNSIGNED) AS ts
                FROM (
                    SELECT cc.case_type_id, MAX(ca.activity_date_time) latest_datetime
                    FROM civicrm_case cc
                    JOIN civicrm_case_activity cca
                        ON cca.case_id = cc.id
                    JOIN civicrm_activity ca
                        ON ca.id = cca.activity_id
                        AND ca.activity_type_id = 16 # Change status
                    GROUP BY cc.case_type_id

                    UNION
                    
                    SELECT cc.case_type_id, MAX(con.modified_date) latest_datetime
                    FROM civicrm_case cc
                    JOIN civicrm_case_contact ccc
                        ON ccc.case_id = cc.id
                    JOIN civicrm_contact con
                        ON con.id = ccc.contact_id
                        AND con.is_deleted = 0
                    GROUP BY cc.case_type_id
                ) x
                GROUP BY case_type_id
                ;
            '''))}

    def get_link(self, record_id):
        return self.link.format(record_id=record_id)

    def _get_latest_timestamp(self):
        return CiviCrmEcrfSource.get_newest_timestamps()[self.case_type_id]

    @property
    def get_custom_tables(self):
        return decode_list_string(self.custom_tables)

    def set_custom_tables(self, value):
        self.custom_tables = encode_list_string(value)

    def _get_query(self):
        joins = " ".join(f"LEFT JOIN {t} ON {t}.entity_id = cc.id" for t in self.get_custom_tables)
        selects = " ".join(f"{t}.*, " for t in self.get_custom_tables)

        return f"""
            SELECT
                cc.id AS civicrm_case_id,
                cc.id AS record,
                con.id AS civicrm_contact_id,
                cvci.nhs_number_1,
                cvci.uhl_s_number_2,
                cc.start_date AS case_start_date,
                con.first_name,
                con.last_name,
                con.gender_id,
                con.birth_date,
                a.postal_code,
                cc.status_id case_status_id,
                w.withdrawal_date,
                {selects}
                GREATEST(
                    COALESCE(s.latest_datetime, 0),
                    COALESCE(CONVERT(DATE_FORMAT(con.modified_date, '%Y%m%d%H%i%S'), UNSIGNED), 0)
                ) AS last_update_timestamp,
                s.latest_datetime,
                con.modified_date
            FROM civicrm_case cc
            JOIN civicrm_case_contact ccc
                ON ccc.case_id = cc.id
            JOIN civicrm_contact con
                ON con.id = ccc.contact_id
                AND con.is_deleted = 0
            LEFT JOIN civicrm_value_contact_ids_1 cvci
                ON cvci.entity_id = con.id
            LEFT JOIN (
                SELECT
                    CASE @id <=> contact_id AND @address_row IS NOT NULL 
                        WHEN TRUE THEN @address_row := @address_row+1 
                        ELSE @address_row := 0 
                    END AS rownum,
                    @id := contact_id AS contact_id,
                    postal_code
                FROM civicrm_address ca
                ORDER BY
                    ca.contact_id, ca.is_primary DESC, ca.id DESC
            ) a
                ON a.contact_id = con.id
                AND a.rownum = 0
            LEFT JOIN (
                SELECT
                    cca.case_id AS civicrm_case_id,
                    MIN(ca.activity_date_time) AS withdrawal_date
                FROM civicrm_case_activity cca
                JOIN civicrm_activity ca
                    ON ca.id = cca.activity_id
                    AND ca.activity_type_id = 16
                    AND ca.is_deleted = 0
                    AND ca.is_current_revision = 1
                AND ca.subject LIKE '% to Withdrawn'
                GROUP BY cca.case_id
            ) w ON w.civicrm_case_id = cc.id
                AND cc.status_id = 8 # withdrawn
            LEFT JOIN (
                SELECT
                    cca.case_id AS civicrm_case_id,
                    CONVERT(DATE_FORMAT(MAX(ca.activity_date_time), '%Y%m%d%H%i%S'), UNSIGNED) latest_datetime
                FROM civicrm_case_activity cca
                JOIN civicrm_activity ca
                    ON ca.id = cca.activity_id
                    AND ca.activity_type_id = 16 # case status changed
                GROUP BY cca.case_id
            ) s ON s.civicrm_case_id = cc.id
            {joins}
            WHERE cc.case_type_id = :case_type_id
                AND cc.is_deleted = 0
                AND GREATEST(
                    COALESCE(s.latest_datetime, 0),
                    COALESCE(CONVERT(DATE_FORMAT(con.modified_date, '%Y%m%d%H%i%S'), UNSIGNED), 0)
                ) > :timestamp
            ;
        """

    def get_participants(self, pid):
        with redcap_engine(CiviCrmInstanceDetail.UHL_LIVE['database_name']) as conn:
            return conn.execute(
                text(self._get_query()),
                case_type_id=self.case_type_id,
                timestamp=pid.latest_timestamp
            )

    def __repr__(self):
        return f'<CiviCRM Ecrf Source: "{self.name}"">'

    def __str__(self):
        return f'CiviCRM: {self.name}'


class ParticipantImportDefinition(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    study_id = db.Column(db.Integer, db.ForeignKey(Study.id))
    study = db.relationship(Study)

    active = db.Column(db.Boolean(), default=False)

    ecrf_source_id = db.Column(db.Integer, db.ForeignKey(EcrfSource.id))
    ecrf_source = db.relationship(EcrfSource, backref=db.backref("participant_import_definitions"))

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

    last_updated_datetime = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    last_updated_by_user_id = db.Column(
        db.Integer,
        db.ForeignKey(User.id),
        default=system_user_id,
        onupdate=system_user_id,
    )
    last_updated_by_user = db.relationship(User)

    _latest_timestamp = column_property(
        select([func.max(EcrfDetail.ecrf_timestamp)]).where(EcrfDetail.participant_import_definition_id==id).scalar_subquery()
    )

    @property
    def latest_timestamp(self):
        return self._latest_timestamp or 0

    @property
    def withdrawn_from_study_values_list(self):
        return decode_list_string(self.withdrawn_from_study_values)

    def set_withdrawn_from_study_values_list(self, value):
        self.withdrawn_from_study_values = encode_list_string(value)

    @property
    def complete_or_expected_values_list(self):
        return decode_list_string(self.complete_or_expected_values)

    def set_complete_or_expected_values_list(self, value):
        self.complete_or_expected_values = encode_list_string(value)

    @property
    def post_withdrawal_keep_samples_values_list(self):
        return decode_list_string(self.post_withdrawal_keep_samples_values)

    def set_post_withdrawal_keep_samples_values_list(self, value):
        self.post_withdrawal_keep_samples_values = encode_list_string(value)

    @property
    def post_withdrawal_keep_data_values_list(self):
        return decode_list_string(self.post_withdrawal_keep_data_values)

    def set_post_withdrawal_keep_data_values_list(self, value):
        self.post_withdrawal_keep_data_values = encode_list_string(value)

    @property
    def brc_opt_out_values_list(self):
        return decode_list_string(self.brc_opt_out_values)

    def set_brc_opt_out_values_list(self, value):
        self.brc_opt_out_values = encode_list_string(value)

    @property
    def excluded_from_analysis_values_list(self):
        return decode_list_string(self.excluded_from_analysis_values)

    def set_excluded_from_analysis_values_list(self, value):
        self.excluded_from_analysis_values = encode_list_string(value)

    @property
    def excluded_from_study_values_list(self):
        return decode_list_string(self.excluded_from_study_values)

    def set_excluded_from_study_values_list(self, value):
        self.excluded_from_study_values = encode_list_string(value)

    @property
    def sex_column_map_dictionary(self):
        return decode_dictionary_string(self.sex_column_map)

    def set_sex_column_map_dictionary(self, map):
        self.sex_column_map = encode_dictionary_string(map)

    @property
    def identities_map_dictionary(self):
        return decode_dictionary_string(self.identities_map)

    def set_identities_map_dictionary(self, map):
        self.identities_map = encode_dictionary_string(map)

    def get_fields(self):
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

    def fill_ecrf(self, participant_details, existing_ecrf):
        if existing_ecrf is None:
            current_app.logger.debug(f'Creating ecrf for participant "{participant_details["record"]}"')
            result = EcrfDetail(
                participant_import_definition_id=self.id,
                ecrf_participant_identifier=participant_details['record'],
            )
            result.identifier_source = EcrfParticipantIdentifierSource(study_id=self.study_id)
        else:
            current_app.logger.debug(f'Updating ecrf for participant: {participant_details["record"]}')
            result = existing_ecrf

        return self._fill_ecrf_details(participant_details, result)

    def extract_identifiers(self, participant_details):
        erec = EcrfRecord(participant_details)

        return [
            {
                'type': type,
                'identifier': erec.get(field),
            }
            for type, field in self.identities_map_dictionary.items()
            if erec.get(field)
        ]

    def _fill_ecrf_details(self, record, ecrf):
        erec = EcrfRecord(record)

        ecrf.recruitment_date = erec.get_parsed_date(self.recruitment_date_column_name)
        ecrf.first_name = erec.get(self.first_name_column_name)
        ecrf.last_name = erec.get(self.last_name_column_name)
        ecrf.postcode = erec.get(self.postcode_column_name)
        ecrf.birth_date = erec.get_parsed_date(self.birth_date_column_name)
        ecrf.sex = self.sex_column_map_dictionary.get(erec.get(self.sex_column_name))
        ecrf.complete_or_expected = erec.get_from_value_array(self.complete_or_expected_column_name, self.complete_or_expected_values_list)
        ecrf.withdrawal_date = erec.get_parsed_date(self.withdrawal_date_column_name)
        ecrf.withdrawn_from_study = erec.get_from_value_array(self.withdrawn_from_study_column_name, self.withdrawn_from_study_values_list)
        ecrf.post_withdrawal_keep_samples = erec.get_from_value_array(self.post_withdrawal_keep_samples_column_name, self.post_withdrawal_keep_samples_values_list)
        ecrf.post_withdrawal_keep_data = erec.get_from_value_array(self.post_withdrawal_keep_data_column_name, self.post_withdrawal_keep_data_values_list)
        ecrf.brc_opt_out = erec.get_from_value_array(self.brc_opt_out_column_name, self.brc_opt_out_values_list)
        ecrf.excluded_from_analysis = erec.get_from_value_array(self.excluded_from_analysis_column_name, self.excluded_from_analysis_values_list)
        ecrf.excluded_from_study = erec.get_from_value_array(self.excluded_from_study_column_name, self.excluded_from_study_values_list)

        return ecrf


class EcrfRecord():
    def __init__(self, record):
        self.record = record
    
    def get(self, column_name):
        if len((column_name or '').strip()) == 0 or column_name not in self.record or self.record[column_name] is None:
            return None
        else:
            if type(self.record[column_name]) == str:
                return self.record[column_name].strip()
            else:
                return self.record[column_name]

    def get_parsed_date(self, column_name):
        return parse_date_or_none(self.get(column_name))

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


class EcrfParticipantIdentifierSource(ParticipantIdentifierSource):
    __tablename__ = 'ecrf_participant_identifier_source'

    participant_identifier_source_id = db.Column(db.Integer, db.ForeignKey('participant_identifier_source.id'), primary_key=True)
    ecrf_detail_id = db.Column(db.Integer, db.ForeignKey(EcrfDetail.id), nullable=False)
    ecrf_detail = db.relationship("EcrfDetail", back_populates="identifier_source")

    __mapper_args__ = {
        'polymorphic_identity':'ecrf_participant_identifier_source',
    }
