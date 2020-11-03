from identity.ecrfs.model import ParticipantImportDefinition, RedcapInstance, RedcapProject
from identity.model import Study


crfs = []


class EcrfDefinition():

    def __init__(self, definition):
        self.crfs = definition['crfs']
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

    def get_partipipant_import_definitions(self, user):
        results = []

        for c in self.crfs:

            study = Study.query.filter_by(name=c['study']).one_or_none()
            ri = RedcapInstance.query.filter_by(name=c['instance']['name']).one_or_none()

            for project in c['projects']:

                rp = RedcapProject.query.filter_by(redcap_instance_id=ri.id, project_id=project).one_or_none()

                if rp is None:
                    continue
                
                pid = ParticipantImportDefinition.query.filter_by(study_id=study.id, ecrf_source_id=rp.id).one_or_none()

                if pid is None:
                    pid = ParticipantImportDefinition(
                        study_id=study.id,
                        ecrf_source_id=rp.id,
                        last_updated_by_user_id=user.id,
                    )

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

                results.append(pid)
        
        return results


import identity.ecrfs.setup.projects