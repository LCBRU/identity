from functools import cache
from random import choice
from identity.model.civicrm import CiviCrmCaseStatus, CiviCrmContact, CiviCrmContactIds, CiviCrmGender, CiviCrmParticipant, CiviCrmCaseContact, CiviCrmParticipantAmazeDetails, CiviCrmParticipantArchiveDetails, CiviCrmParticipantBioresourceDetails, CiviCrmParticipantBioresourceSubStudyDetails, CiviCrmParticipantBioresourceWithdrawalDetails, CiviCrmParticipantBraveDetails, CiviCrmParticipantBriccsDetails, CiviCrmParticipantCardiometDetails, CiviCrmParticipantDiscordanceDetails, CiviCrmParticipantDreamDetails, CiviCrmParticipantEmmace4Details, CiviCrmParticipantFastDetails, CiviCrmParticipantFoamiDetails, CiviCrmParticipantGenvascDetails, CiviCrmParticipantGenvascInvoiceDetails, CiviCrmParticipantGenvascWithdrawalDetails, CiviCrmParticipantGlobalLeadersDetails, CiviCrmParticipantGraphic2Details, CiviCrmParticipantIndapamideDetails, CiviCrmParticipantIntervalDetails, CiviCrmParticipantLentenDetails, CiviCrmParticipantLimbDetails, CiviCrmParticipantNationalBioresourceDetails, CiviCrmParticipantOmicsDetails, CiviCrmParticipantPredictDetails, CiviCrmParticipantPreeclampsiaDetails, CiviCrmParticipantScadDetails, CiviCrmParticipantScadRegisterDetails, CiviCrmParticipantSpiralDetails, CiviCrmParticipantTmaoDetails, CiviCrmStudy
from faker.providers import BaseProvider
from lbrc_flask.pytest.faker import FakeCreator, FakeCreatorArgs, randint


class CiviCrmGenderCreator(FakeCreator):
    DEFAULT_VALUES = [
        {
            "value": 2,
            "name": "Male",
            "label": "Male"
        },
        {
            "value": 1,
            "name": "Female",
            "label": "Female"
        },
    ]

    @property
    def cls(self):
        return CiviCrmGender

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            value = args.get('value', self.faker.unique.pyint()),
            name = args.get('name', self.faker.pystr(min_chars=5, max_chars=100)),
        )

        params['label'] = args.get('label', params['name'])

        return self.cls(**params)


class CiviCrmCaseStatusCreator(FakeCreator):
    DEFAULT_VALUES = [
        {
            "value": 1,
            "name": "Open",
            "label": "Open"
        },
        {
            "value": 2,
            "name": "Closed",
            "label": "Closed"
        },
        {
            "value": 3,
            "name": "Recruitment Pending",
            "label": "Recruitment Pending"
        },
        {
            "value": 4,
            "name": "Recruited",
            "label": "Recruited"
        },
        {
            "value": 5,
            "name": "Available for Cohort",
            "label": "Available for Cohort"
        },
    ]

    @property
    def cls(self):
        return CiviCrmCaseStatus

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            value = args.get('value', self.faker.unique.pyint()),
            name = args.get('name', self.faker.pystr(min_chars=5, max_chars=100)),
        )

        params['label'] = args.get('label', params['name'])

        return self.cls(**params)


class CiviCrmStudyCreator(FakeCreator):
    DEFAULT_VALUES = [
        {"name": "Amaze"},
        {"name": "Bioresource"},
        {"name": "Brave"},
        {"name": "BRICCS"},
        {"name": "Cardiomet"},
        {"name": "Discordance"},
        {"name": "Dream"},
        {"name": "EMMACE 4"},
        {"name": "FAST"},
        {"name": "FOAMI"},
        {"name": "GENVASC"},
        {"name": "Global Leaders"},
        {"name": "Graphic 2"},
        {"name": "Indapamide"},
        {"name": "Interval"},
        {"name": "Lenten"},
        {"name": "LIMB"},
        {"name": "National Bioresource"},
        {"name": "OMICS"},
        {"name": "Predict"},
        {"name": "Preeclampsia"},
        {"name": "SCAD"},
        {"name": "SPIRAL"},
        {"name": "TMAO"},
    ]

    @property
    def cls(self):
        return CiviCrmStudy

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            name = args.get('name', self.faker.unique.word()),
            description = args.get('description', self.faker.sentence()),
            is_active = args.get('is_active', self.faker.pybool()),
        )

        params['title'] = args.get('title', params['name'])

        return self.cls(**params)


class CiviCrmContactCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmContact

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            contact_type='Subject',
            contact_sub_type='Subject',
            first_name=self.faker.first_name(),
            middle_name=self.faker.first_name(),
            last_name=self.faker.last_name(),
            birth_date=self.faker.date_object(),
            is_deleted=(randint(1, 10) > 9),
        )

        gender = args.get('gender', self.faker.civicrm_gender().choice_from_db())
        if gender is not None:
            params['gender_id'] = gender.value

        return self.cls(**params)


class CiviCrmCaseContactCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmCaseContact

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict()

        args.set_params_with_object(params, 'case', creator=self.faker.civicrm_participant())
        args.set_params_with_object(params, 'contact', creator=self.faker.civicrm_contact())

        return self.cls(**params)


class CiviCrmContactIdsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmContactIds

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            nhs_number = args.get('nhs_number', self.faker.unique.nhs_number()),
            uhl_system_number = args.get('uhl_system_number', self.faker.unique.uhl_system_number()),
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact is not None:
            params['entity_id'] = contact.id

        return self.cls(**params)
    

class CiviCrmParticipantAmazeDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantAmazeDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier = args.get('study_identifier', f'AM{self.faker.unique.pyint(10000, 99999)}',),
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantBioresourceSubStudyDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantBioresourceSubStudyDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            sub_study = args.get('sub_study', self.faker.unique.word().title()),
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantBraveDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantBraveDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'BR{self.faker.unique.pyint(10000, 99999)}',
            source_study=self.faker.unique.word().title(),
            briccs_id=f'BPt{self.faker.unique.pyint(10000, 99999)}',
            family_id=f'BRFm{self.faker.unique.pyint(10000, 99999)}',
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantBriccsDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantBriccsDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'BPt{self.faker.unique.pyint(10000, 99999)}',
            interview_date_and_time=self.faker.date_time(),
            interviewer=self.faker.name(),
            interview_status=choice(['Good', 'Bad', 'Indifferent']),
            consent_understands_consent=choice([True, False]),
            consent_blood_and_urine=choice([True, False]),
            consent_briccs_database=choice([True, False]),
            consent_further_contact=choice([True, False]),
            consent_understands_withdrawal=choice([True, False]),
            recruitment_type=choice(['Index', 'Healthy Volunteer']),
            invitation_for=choice(['Sutin', 'Nustin']),
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantCardiometDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantCardiometDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'Cm{self.faker.unique.pyint(10000, 99999)}',
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantDiscordanceDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantDiscordanceDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'Dis{self.faker.unique.pyint(10000, 99999)}',
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantDreamDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantDreamDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'DR{self.faker.unique.pyint(10000, 99999)}',
            consent_to_participate_in_dream=choice([True, False]),
            consent_to_store_dream_study_sam=choice([True, False]),
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantEmmace4DetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantEmmace4Details

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'Em{self.faker.unique.pyint(10000, 99999)}',
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantFastDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantFastDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'Fs{self.faker.unique.pyint(10000, 99999)}',
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantFoamiDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantFoamiDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'Fo{self.faker.unique.pyint(10000, 99999)}',
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantGenvascInvoiceDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantGenvascInvoiceDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            invoice_year=f'{self.faker.pyint(2015, 2020)}',
            invoice_quarter=f'Q{self.faker.pyint(1, 4)}',
            processed_by=self.faker.name(),
            processed_date=self.faker.date_time(),
            reimbursed_status=choice(['Reimbursed', 'Duplicate', 'Error']),
            notes=self.faker.paragraph(),
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantGenvascDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantGenvascDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'GPt{self.faker.unique.pyint(10000, 99999)}',
            consent_q1=choice([True, False]),
            consent_q2=choice([True, False]),
            consent_q3=choice([True, False]),
            consent_q4=choice([True, False]),
            consent_q5=choice([True, False]),
            consent_q6=choice([True, False]),
            consent_q7=choice([True, False]),
            post_code=self.faker.postcode(),
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantGenvascWithdrawalDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantGenvascWithdrawalDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            withdrawal_status=choice(['Keep', 'Destroy']),
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantGlobalLeadersDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantGlobalLeadersDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'GL{self.faker.unique.pyint(10000, 99999)}',
            treatment_arm=choice('ABC'),
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantGraphic2DetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantGraphic2Details

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'Gfx{self.faker.unique.pyint(10000, 99999)}',
            graphic_lab_id=f'GfxL{self.faker.unique.pyint(10000, 99999)}',
            graphic_family_id=f'GfxF{self.faker.unique.pyint(10000, 99999)}',
            consent_for_further_studies=choice([True, False]),
            g1_blood_consent=choice([True, False]),
            pre_consent_to_graphic_2=choice([True, False]),
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantIndapamideDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantIndapamideDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'Ind{self.faker.unique.pyint(10000, 99999)}',
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantIntervalDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantIntervalDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'Int{self.faker.unique.pyint(10000, 99999)}',
            consent_date=self.faker.date(),
            consent_version=choice(['v1', 'v2', 'v3']),
            consent_leaflet=choice(['v1', 'v2']),
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantLentenDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantLentenDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'Len{self.faker.unique.pyint(10000, 99999)}',
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantLimbDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantLimbDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'Lmb{self.faker.unique.pyint(10000, 99999)}',
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantNationalBioresourceDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantNationalBioresourceDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'NBr{self.faker.unique.pyint(10000, 99999)}',
            leicester_bioresource_id=f'Br{self.faker.unique.pyint(10000, 99999)}',
            legacy_bioresource_id=f'LBr{self.faker.unique.pyint(10000, 99999)}',
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantBioresourceDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantBioresourceDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'Br{self.faker.unique.pyint(10000, 99999)}',
            date_of_consent=self.faker.date_time(),
            nihr_bioresource_consent_q1=choice([True, False]),
            nihr_bioresource_consent_q2=choice([True, False]),
            nihr_bioresource_consent_q3=choice([True, False]),
            nihr_bioresource_consent_q4=choice([True, False]),
            nihr_bioresource_consent_q5=choice([True, False]),
            nihr_bioresource_consent_q6=choice([True, False]),
            nihr_bioresource_legacy_id=f'LBr{self.faker.unique.pyint(10000, 99999)}',
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantBioresourceWithdrawalDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantBioresourceWithdrawalDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            nihr_bioresource_withdrawal_stat=choice(['Keep', 'Destroy']),
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantOmicsDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantOmicsDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'Om{self.faker.unique.pyint(10000, 99999)}',
            sample_source_study=self.faker.word().title(),
            failed_qc=choice([True, False]),
            date_data_received=self.faker.date_time(),
            omics_type=choice(['Full', 'Panel']),
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantPredictDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantPredictDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'Pr{self.faker.unique.pyint(10000, 99999)}',
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantPreeclampsiaDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantPreeclampsiaDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'Pre{self.faker.unique.pyint(10000, 99999)}',
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantScadDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantScadDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'Sc{self.faker.unique.pyint(10000, 99999)}',
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
            consent_date=self.faker.date_time(),
            briccs_id=f'Br{self.faker.unique.pyint(10000, 99999)}',
            survey_reference=f'ScR{self.faker.unique.pyint(10000, 99999)}',
            scad_visit_id=f'ScV{self.faker.unique.pyint(10000, 99999)}',
            recruitment_type=choice(['Index', 'Healthy Volunteer']),
            second_scad_survey_id=f'ScR{self.faker.unique.pyint(10000, 99999)}',
            scad_registry_id=f'ScRef{self.faker.unique.pyint(10000, 99999)}',
            family_id=f'ScFm{self.faker.unique.pyint(10000, 99999)}',
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantScadRegisterDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantScadRegisterDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'ScRef{self.faker.unique.pyint(10000, 99999)}',
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantSpiralDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantSpiralDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'Spi{self.faker.unique.pyint(10000, 99999)}',
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantTmaoDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantTmaoDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            study_identifier=f'Tm{self.faker.unique.pyint(10000, 99999)}',
            tmao_consent_has_read_informatio=choice([True, False]),
            tmao_consent_understands_withdra=choice([True, False]),
            tmao_consent_permission_to_acces=choice([True, False]),
            tmao_consent_gp_informed=choice([True, False]),
            tmao_consent_to_enrol=choice([True, False]),
            tmao_consent_to_store_blood=choice([True, False]),
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantArchiveDetailsCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipantArchiveDetails

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            box_barcode=f'Arxiv{self.faker.unique.pyint(10000, 99999)}',
        )

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        if contact:
            params['entity_id'] = contact.id

        return self.cls(**params)


class CiviCrmParticipantCreator(FakeCreator):
    @property
    def cls(self):
        return CiviCrmParticipant

    def _create_item(self, save, args: FakeCreatorArgs):
        params = dict(
            subject = args.get('subject', self.faker.unique.license_plate()),
            start_date = args.get('start_date', self.faker.date_object()),
            end_date = args.get('end_date', self.faker.date_object()),
            is_deleted = args.get('is_deleted', (randint(1, 10) > 9)),
        )

        args.set_params_with_object(params, 'study', creator=self.faker.civicrm_study())
        args.set_params_with_object(params, 'status', creator=self.faker.civicrm_case_status())

        contact = args.get('contact', self.faker.civicrm_contact().get(save=save))

        result = self.cls(**params)

        if contact is not None:
            self.faker.civicrm_case_contact().get(save=save, case=result, contact=contact)
            contact_ids = args.get('civicrm_contact_ids', self.faker.civicrm_contact_ids().get(save=save, contact=contact))
            contact.contact_ids = contact_ids

            if randint(1, 10) > 9:
                self.faker.civicrm_participant_archive_details().get(save=save, contact=contact)

        study = None
        if 'study' in args:
            study = args.get('study')
        elif 'study_id' in args:
            study = self.faker.civicrm_study().get_by_id(args.get('study_id'))

        if contact and study:
            match study.name:
                case "Amaze":
                    self.faker.civicrm_participant_amaze_details().get(save=save, contact=contact)
                case "Bioresource":
                    self.faker.civicrm_participant_bioresource_substudy_details().get(save=save, contact=contact)
                    self.faker.civicrm_participant_bioresource_details().get(save=save, contact=contact)
                    if randint(1, 10) > 9:
                        self.faker.civicrm_participant_bioresource_withdrawal_details().get(save=save, contact=contact)
                case "Brave":
                    self.faker.civicrm_participant_brave_details().get(save=save, contact=contact)                
                case "BRICCS":
                    self.faker.civicrm_participant_briccs_details().get(save=save, contact=contact)
                case "Cardiomet":
                    self.faker.civicrm_participant_cardiomet_details().get(save=save, contact=contact)
                case "Discordance":
                    self.faker.civicrm_participant_discordance_details().get(save=save, contact=contact)
                case "Dream":
                    self.faker.civicrm_participant_dream_details().get(save=save, contact=contact)
                case "EMMACE 4":
                    self.faker.civicrm_participant_emmace4_details().get(save=save, contact=contact)
                case "FAST":
                    self.faker.civicrm_participant_fast_details().get(save=save, contact=contact)
                case "FOAMI":
                    self.faker.civicrm_participant_foami_details().get(save=save, contact=contact)
                case "GENVASC":
                    self.faker.civicrm_participant_genvasc_invoice_details().get(save=save, contact=contact)
                    self.faker.civicrm_participant_genvasc_details().get(save=save, contact=contact)
                    if randint(1, 10) > 9:
                        self.faker.civicrm_participant_genvasc_withdrawal_details().get(save=save, contact=contact)
                case "Global Leaders":
                    self.faker.civicrm_participant_global_leaders_details().get(save=save, contact=contact)
                case "Graphic 2":
                    self.faker.civicrm_participant_graphic2_details().get(save=save, contact=contact)
                case "Indapamide":
                    self.faker.civicrm_participant_indapamide_details().get(save=save, contact=contact)
                case "Interval":
                    self.faker.civicrm_participant_interval_details().get(save=save, contact=contact)
                case "Lenten":
                    self.faker.civicrm_participant_lenten_details().get(save=save, contact=contact)
                case "LIMB":
                    self.faker.civicrm_participant_limb_details().get(save=save, contact=contact)
                case "National Bioresource":
                    self.faker.civicrm_participant_national_bioresource_details().get(save=save, contact=contact)
                case "OMICS":
                    self.faker.civicrm_participant_omics_details().get(save=save, contact=contact)
                case "Predict":
                    self.faker.civicrm_participant_predict_details().get(save=save, contact=contact)
                case "Preeclampsia":
                    self.faker.civicrm_participant_Preeclampsia_details().get(save=save, contact=contact)
                case "SCAD":
                    self.faker.civicrm_participant_scad_details().get(save=save, contact=contact)
                    self.faker.civicrm_participant_scad_register_details().get(save=save, contact=contact)
                case "SPIRAL":
                    self.faker.civicrm_participant_spiral_details().get(save=save, contact=contact)
                case "TMAO":
                    self.faker.civicrm_participant_tmao_details().get(save=save, contact=contact)

        return result


class CivicrmProvider(BaseProvider):
    @cache
    def civicrm_gender(self):
        return CiviCrmGenderCreator(self)

    @cache
    def civicrm_case_status(self):
        return CiviCrmCaseStatusCreator(self)

    @cache
    def civicrm_contact(self):
        self.civicrm_gender().create_defaults()

        return CiviCrmContactCreator(self)  
    
    @cache
    def civicrm_case_contact(self):
        return CiviCrmCaseContactCreator(self)

    @cache
    def civicrm_participant(self):
        return CiviCrmParticipantCreator(self)

    @cache
    def civicrm_study(self):
        return CiviCrmStudyCreator(self)

    @cache
    def civicrm_contact_ids(self):
        return CiviCrmContactIdsCreator(self)
    
    @cache
    def civicrm_participant_amaze_details(self):
        return CiviCrmParticipantAmazeDetailsCreator(self)

    @cache
    def civicrm_participant_archive_details(self):
        return CiviCrmParticipantArchiveDetailsCreator(self)

    @cache
    def civicrm_participant_bioresource_substudy_details(self):
        return CiviCrmParticipantBioresourceSubStudyDetailsCreator(self)

    @cache
    def civicrm_participant_brave_details(self):
        return CiviCrmParticipantBraveDetailsCreator(self)

    @cache
    def civicrm_participant_briccs_details(self):
        return CiviCrmParticipantBriccsDetailsCreator(self)

    @cache
    def civicrm_participant_cardiomet_details(self):
        return CiviCrmParticipantCardiometDetailsCreator(self)

    @cache
    def civicrm_participant_discordance_details(self):
        return CiviCrmParticipantDiscordanceDetailsCreator(self)

    @cache
    def civicrm_participant_dream_details(self):
        return CiviCrmParticipantDreamDetailsCreator(self)

    @cache
    def civicrm_participant_emmace4_details(self):
        return CiviCrmParticipantEmmace4DetailsCreator(self)

    @cache
    def civicrm_participant_fast_details(self):
        return CiviCrmParticipantFastDetailsCreator(self)

    @cache
    def civicrm_participant_foami_details(self):
        return CiviCrmParticipantFoamiDetailsCreator(self)

    @cache
    def civicrm_participant_genvasc_invoice_details(self):
        return CiviCrmParticipantGenvascInvoiceDetailsCreator(self)

    @cache
    def civicrm_participant_genvasc_details(self):
        return CiviCrmParticipantGenvascDetailsCreator(self)

    @cache
    def civicrm_participant_genvasc_withdrawal_details(self):
        return CiviCrmParticipantGenvascWithdrawalDetailsCreator(self)

    @cache
    def civicrm_participant_global_leaders_details(self):
        return CiviCrmParticipantGlobalLeadersDetailsCreator(self)

    @cache
    def civicrm_participant_graphic2_details(self):
        return CiviCrmParticipantGraphic2DetailsCreator(self)

    @cache
    def civicrm_participant_indapamide_details(self):
        return CiviCrmParticipantIndapamideDetailsCreator(self)

    @cache
    def civicrm_participant_interval_details(self):
        return CiviCrmParticipantIntervalDetailsCreator(self)

    @cache
    def civicrm_participant_lenten_details(self):
        return CiviCrmParticipantLentenDetailsCreator(self)

    @cache
    def civicrm_participant_limb_details(self):
        return CiviCrmParticipantLimbDetailsCreator(self)

    @cache
    def civicrm_participant_national_bioresource_details(self):
        return CiviCrmParticipantNationalBioresourceDetailsCreator(self)

    @cache
    def civicrm_participant_bioresource_details(self):
        return CiviCrmParticipantBioresourceDetailsCreator(self)

    @cache
    def civicrm_participant_bioresource_withdrawal_details(self):
        return CiviCrmParticipantBioresourceWithdrawalDetailsCreator(self)

    @cache
    def civicrm_participant_omics_details(self):
        return CiviCrmParticipantOmicsDetailsCreator(self)

    @cache
    def civicrm_participant_predict_details(self):
        return CiviCrmParticipantPredictDetailsCreator(self)

    @cache
    def civicrm_participant_Preeclampsia_details(self):
        return CiviCrmParticipantPreeclampsiaDetailsCreator(self)

    @cache
    def civicrm_participant_scad_details(self):
        return CiviCrmParticipantScadDetailsCreator(self)

    @cache
    def civicrm_participant_scad_register_details(self):
        return CiviCrmParticipantScadRegisterDetailsCreator(self)

    @cache
    def civicrm_participant_spiral_details(self):
        return CiviCrmParticipantSpiralDetailsCreator(self)

    @cache
    def civicrm_participant_tmao_details(self):
        return CiviCrmParticipantTmaoDetailsCreator(self)
