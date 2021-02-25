class CiviCrmInstanceDetail():
    UHL_LIVE = {
        'name': 'CiviCRM UHL Live',
        'database_name': 'civicrmlive_docker4716',
        'base_url': 'https://lcbru.xuhl-tr.nhs.uk/',
    }

    def all_instances(self):
        return [getattr(self, f) for f in dir(self) if not callable(getattr(self,f)) and not f.startswith('__')]
