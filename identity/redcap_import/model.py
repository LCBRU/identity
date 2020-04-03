from dateutil.parser import parse
from flask import current_app
from identity.model.id import (
    ParticipantIdentifier,
    ParticipantIdentifierType,
)
from identity.model import EcrfDetail, RedcapProject
from identity.database import db


class ParticipantImportStrategy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "ParticipantImportStrategy",
        "polymorphic_on": type,
    }

    def __init__(self, fields):
        self._fields = fields

    def get_query(self):
        group_concats = ", ".join(f"GROUP_CONCAT(DISTINCT CASE WHEN field_name = '{f}' THEN VALUE ELSE NULL END) AS {f}" for f in self._fields)
        ins = ", ".join((f"'{f}'" for f in self._fields))

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

    def fill_ecrf(self, record, existing_ecrf):

        if existing_ecrf is None:
            current_app.logger.info(f'Creating ecrf for participant "{record["record"]}"')
            result = EcrfDetail(
                project_id=record['project_id'],
                ecrf_participant_identifier=record['record'],
            )
        else:
            current_app.logger.info(f'Updating ecrf for participant: {record["record"]}')
            result = existing_ecrf

        return self._fill_ecrf_details(record, result)

    
    def fill_identifiers(self, record, ecrf, user):
        ecrf.identifiers.clear()

        for id_type_name, identifier in self._get_identifier_type_fields().items():
            if not record[identifier]:
                continue

            id_type = ParticipantIdentifierType.get_or_create_type(id_type_name, user)

            i = ParticipantIdentifier.query.filter_by(
                participant_identifier_type_id=id_type.id,
                identifier=record[identifier].strip(),                
            ).one_or_none()

            if i is None:
                i = ParticipantIdentifier(
                    participant_identifier_type_id=id_type.id,
                    identifier=record[identifier].strip(),
                    last_updated_by_user_id=user.id,
                )
            
            current_app.logger.info(i)

            ecrf.identifiers.add(i)

    
    # Abstract Methods

    def _fill_ecrf_details(self, record, ecrf):
        pass

    def _get_identifier_type_fields(self):
        return {}


class BriccsParticipantImportStrategy(ParticipantImportStrategy):
    __mapper_args__ = {
        "polymorphic_identity": 'Briccs Participant Import Strategy',
    }

    def __init__(self):
        super().__init__([
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
        ])
    
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
            'briccs_id': 'record',
            'nhs_number': 'nhs_number',
            'uhl_system_number': 's_number',
        }