from enum import Enum

class REDCapInstance():
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
    UOL_RECHARGE = {
        'name': 'UoL recharge',
        'database_name': 'uol_recharge_redcap',
        'base_url': 'https://recharge.lbrc.le.ac.uk',
        'version': '7.6.1',
    }
    UOL_EDEN = {
        'name': 'UoL eden',
        'database_name': 'uol_eden_redcap',
        'base_url': 'https://eden.lbrc.le.ac.uk/',
        'version': '7.6.1',
    }

    def all_instances(self):
        return [getattr(self, f) for f in dir(self) if not callable(getattr(self,f)) and not f.startswith('__')]
