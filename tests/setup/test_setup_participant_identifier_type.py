from identity.model.id import ParticipantIdentifierType
import pytest
from identity.model import Study
from identity.setup import create_base_data


@pytest.mark.parametrize(
    "id_name",
    [
        ('study_participant_id'),
        ('alleviate_id'),
        ('briccs_id'),
        ('cvlprit_id'),
        ('cvlprit_local_id'),
        ('pilot_id'),
        ('dream_id'),
        ('bioresource_id'),
        ('graphic2_id'),
        ('tmao_id'),
        ('brave_id'),
        ('nhs_number'),
        ('uhl_system_number'),
    ],
)
def test__setup__labelpacks(client, faker, id_name):
    create_base_data()

    assert ParticipantIdentifierType.query.filter_by(name=id_name).one_or_none() is not None

