from identity.setup.studies import StudyName
from identity.redcap.setup.standard import STANDARD_SEX_MAP, STANDARD_STATUS, STANDARD_WITHDRAWAL
from identity.model.id import ParticipantIdentifierType


VASCEGENS = {
    'crfs': [
        {
            'instance': 'UoL CRF',
            'study': StudyName.VasCeGenS,
            'projects': [19],
        },
    ],

    'sex_column_name': 'gender',
    **STANDARD_SEX_MAP,

    'identity_map': {
        ParticipantIdentifierType.__VASCEGENS_ID__: 'record',
    }
}
