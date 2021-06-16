import copy

from lbrc_flask.security import get_system_user
from identity.setup.participant_identifier_types import ParticipantIdentifierTypeName
from identity.model.sex import SexName
from identity.ecrfs.model import CiviCrmEcrfSource, CustomEcrfSource, ParticipantImportDefinition, RedcapInstance, RedcapProject
from identity.model import Study
from lbrc_flask.database import db


crfs = []


class EcrfDefinition():

    def __init__(self, definition):
        self.crfs = definition['crfs']
        self.active = definition.get('active', False)
        self.recruitment_date_column_name = definition.get('recruitment_date_column_name', None)
        self.first_name_column_name = definition.get('first_name_column_name', None)
        self.last_name_column_name = definition.get('last_name_column_name', None)
        self.postcode_column_name = definition.get('postcode_column_name', None)
        self.birth_date_column_name = definition.get('birth_date_column_name', None)
        self.withdrawal_date_column_name = definition.get('withdrawal_date_column_name', None)
        self.withdrawn_from_study_column_name = definition.get('withdrawn_from_study_column_name', None)
        self.withdrawn_from_study_values = definition.get('withdrawn_from_study_values', None)
        self.sex_column_name = definition.get('sex_column_name', None)
        self.sex_column_map = definition.get('sex_column_map', None)
        self.complete_or_expected_column_name = definition.get('complete_or_expected_column_name', None)
        self.complete_or_expected_values = definition.get('complete_or_expected_values', None)
        self.post_withdrawal_keep_samples_column_name = definition.get('post_withdrawal_keep_samples_column_name', None)
        self.post_withdrawal_keep_samples_values = definition.get('post_withdrawal_keep_samples_values', None)
        self.post_withdrawal_keep_data_column_name = definition.get('post_withdrawal_keep_data_column_name', None)
        self.post_withdrawal_keep_data_values = definition.get('post_withdrawal_keep_data_values', None)
        self.brc_opt_out_column_name = definition.get('brc_opt_out_column_name', None)
        self.brc_opt_out_values = definition.get('brc_opt_out_values', None)
        self.excluded_from_analysis_column_name = definition.get('excluded_from_analysis_column_name', None)
        self.excluded_from_analysis_values = definition.get('excluded_from_analysis_values', None)
        self.excluded_from_study_column_name = definition.get('excluded_from_study_column_name', None)
        self.excluded_from_study_values = definition.get('excluded_from_study_values', None)
        self.identity_map = definition.get('identity_map', None)

    def get_ecrf_sources(self, crf_definition):
        pass

    def get_partipipant_import_definitions(self):
        results = []

        for c in self.crfs:
            study = Study.query.filter_by(name=c['study']).one_or_none()

            for source in self.get_ecrf_sources(c):
                pid = ParticipantImportDefinition.query.filter_by(study_id=study.id, ecrf_source_id=source.id).one_or_none()

                if pid is None:
                    pid = ParticipantImportDefinition(
                        study_id=study.id,
                        ecrf_source_id=source.id,
                    )

                pid.active = self.active
                pid.recruitment_date_column_name = self.recruitment_date_column_name
                pid.first_name_column_name = self.first_name_column_name
                pid.last_name_column_name = self.last_name_column_name
                pid.postcode_column_name = self.postcode_column_name
                pid.birth_date_column_name = self.birth_date_column_name
                pid.withdrawal_date_column_name = self.withdrawal_date_column_name
                pid.withdrawn_from_study_column_name = self.withdrawn_from_study_column_name
                pid.set_withdrawn_from_study_values_list(self.withdrawn_from_study_values)
                pid.sex_column_name = self.sex_column_name
                pid.set_sex_column_map_dictionary(self.sex_column_map)
                pid.complete_or_expected_column_name = self.complete_or_expected_column_name
                pid.set_complete_or_expected_values_list(self.complete_or_expected_values)
                pid.post_withdrawal_keep_samples_column_name = self.post_withdrawal_keep_samples_column_name
                pid.set_post_withdrawal_keep_samples_values_list(self.post_withdrawal_keep_samples_values)
                pid.post_withdrawal_keep_data_column_name = self.post_withdrawal_keep_data_column_name
                pid.set_post_withdrawal_keep_data_values_list(self.post_withdrawal_keep_data_values)
                pid.brc_opt_out_column_name = self.brc_opt_out_column_name
                pid.set_brc_opt_out_values_list(self.brc_opt_out_values)
                pid.excluded_from_analysis_column_name = self.excluded_from_analysis_column_name
                pid.set_excluded_from_analysis_values_list(self.excluded_from_analysis_values)
                pid.excluded_from_study_column_name = self.excluded_from_study_column_name
                pid.set_excluded_from_study_values_list(self.excluded_from_study_values)
                pid.set_identities_map_dictionary(self.identity_map)
                pid.last_updated_by_user = get_system_user()

                results.append(pid)
        
        return results


class RedCapEcrfDefinition(EcrfDefinition):

    def get_ecrf_sources(self, crf_definition):
        results = []

        ri = RedcapInstance.query.filter_by(name=crf_definition['instance']['name']).one_or_none()

        for project in crf_definition['projects']:
            rp = RedcapProject.query.filter_by(redcap_instance_id=ri.id, project_id=project).one_or_none()

            if rp is not None:
                results.append(rp)
        
        return results


class CustomEcrfDefinition(EcrfDefinition):

    def get_ecrf_sources(self, crf_definition):
        ced = CustomEcrfSource.query.filter_by(name=crf_definition['name']).one_or_none()

        if ced is None:
            ced = CustomEcrfSource(
                name=crf_definition['name'],
            )
        
        ced.database_name = crf_definition['database_name']
        ced.data_query = crf_definition['data_query']
        ced.most_recent_timestamp_query = crf_definition['most_recent_timestamp_query']
        ced.link = crf_definition['link']

        db.session.add(ced)

        return [ced]


class CiviCrmEcrfDefinition(EcrfDefinition):

    default_config = {
        'recruitment_date_column_name': 'case_start_date',
        'first_name_column_name': 'first_name',
        'last_name_column_name': 'last_name',
        'postcode_column_name': 'postal_code',
        'birth_date_column_name': 'birth_date',
        'withdrawal_date_column_name': 'withdrawal_date',
        'withdrawn_from_study_column_name': 'case_status_id',
        'withdrawn_from_study_values': ['8'],
        'sex_column_name': 'gender_id',
        'set_sex_column_map_dictionary': {
            '1': SexName.FEMALE,
            '2': SexName.MALE,
        },
        'complete_or_expected_column_name': 'case_status_id',
        'complete_or_expected_values': ['6', '10', '5'],
        'excluded_from_analysis_column_name': 'case_status_id',
        'excluded_from_analysis_values': ['9'],
        'excluded_from_study_column_name': 'case_status_id',
        'excluded_from_study_values': ['9'],

        'identity_map': {
            ParticipantIdentifierTypeName.UHL_SYSTEM_NUMBER: 'uhl_s_number_2',
            ParticipantIdentifierTypeName.NHS_NUMBER: 'nhs_number_1',
            ParticipantIdentifierTypeName.CIVICRM_CONTACT_ID: 'civicrm_contact_id',
            ParticipantIdentifierTypeName.CIVICRM_CASE_ID: 'civicrm_case_id',
        }

    }

    def __init__(self, config, id_config):
        c = copy.deepcopy(self.default_config)
        c.update(config)
        c['identity_map'].update(id_config)

        super().__init__(c)
 
    def get_ecrf_sources(self, crf_definition):
        ced = CiviCrmEcrfSource.query.filter_by(name=crf_definition['name']).one_or_none()

        if ced is None:
            ced = CiviCrmEcrfSource(
                name=crf_definition['name'],
            )
        
        ced.case_type_id = crf_definition['case_type_id']
        ced.set_custom_tables(crf_definition['custom_tables'])

        db.session.add(ced)

        return [ced]


import identity.ecrfs.setup.projects