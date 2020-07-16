from enum import Enum

class ParticipantIdentifierTypeName():
    STUDY_PARTICIPANT_ID = 'study_participant_id'
    ALLEVIATE_ID = 'alleviate_id'
    BRICCS_ID = 'briccs_id'
    CVLPRIT_ID = 'cvlprit_id'
    CVLPRIT_LOCAL_ID = 'cvlprit_local_id'
    PILOT_ID = 'pilot_id'
    DREAM_ID = 'dream_id'
    BIORESOURCE_ID = 'bioresource_id'
    GRAPHIC2_ID = 'graphic2_id'
    TMAO_ID = 'tmao_id'
    BRAVE_ID = 'brave_id'
    NHS_NUMBER = 'nhs_number'
    UHL_SYSTEM_NUMBER = 'uhl_system_number'


    def all_types(self):
        return [getattr(self, f) for f in dir(self) if not callable(getattr(self,f)) and not f.startswith('__')]