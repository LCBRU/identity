from enum import Enum

class REDCapInstanceDetail():
    UHL_LIVE = {
        'name': 'UHL Live',
        'database_name': 'redcap6170_briccs',
        'base_url': 'https://briccs.xuhl-tr.nhs.uk/redcap',
        'version': '7.2.2',
    }
    UHL_HSCN = {
        'name': 'UHL HSCN',
        'database_name': 'redcap6170_briccsext',
        'base_url': 'https://uhlbriccsext01.xuhl-tr.nhs.uk/redcap',
        'version': '7.2.2',
    }
    GENVASC = {
        'name': 'GENVASC',
        'database_name': 'redcap_genvasc',
        'base_url': 'https://genvasc.uhl-tr.nhs.uk/redcap',
        'version': '9.1.15',
    }
    UOL_CRF = {
        'name': 'UoL CRF',
        'database_name': 'uol_crf_redcap',
        'base_url': 'https://crf.lcbru.le.ac.uk',
        'version': '7.2.2',
    }
    UOL_INTERNET = {
        'name': 'UoL Internet',
        'database_name': 'uol_survey_redcap',
        'base_url': 'https://redcap.lcbru.le.ac.uk',
        'version': '7.2.2',
    }
    # NATIONAL = {
    #     'name': 'National',
    #     'database_name': 'redcap_national',
    #     'base_url': 'https://brc.uhl-tr.nhs.uk/',
    #     'version': '9.1.15',
    # }

    def all_instances(self):
        return [getattr(self, f) for f in dir(self) if not callable(getattr(self,f)) and not f.startswith('__')]
