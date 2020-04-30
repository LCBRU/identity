from identity.model.id import StudyIdSpecification


ID_TYPE_PARTICIPANT = "HCVPt"


class HicCovidIdSpecification(StudyIdSpecification):
    def __init__(self):
        super().__init__(
            study_name='HIC Covid 19',
            pseudo_identifier_types=[
                {ID_TYPE_PARTICIPANT: 'HIC Covid 19 Participants'},
            ],
        )
