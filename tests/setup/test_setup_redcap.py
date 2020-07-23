from identity.redcap.model import RedcapInstance
import pytest
from identity.setup import create_base_data


@pytest.mark.parametrize(
    "instance, database_name, base_url, version",
    [
        (
            'UHL Live',
            'redcap6170_briccs',
            'https://briccs.xuhl-tr.nhs.uk/redcap',
            '7.2.2',
        ),
        (
            'UHL HSCN',
            'redcap6170_briccsext',
            'https://uhlbriccsext01.xuhl-tr.nhs.uk/redcap',
            '7.2.2',
        ),
        (
            'GENVASC',
            'redcap_genvasc',
            'https://genvasc.uhl-tr.nhs.uk/redcap',
            '9.1.15',
        ),
        (
            'UoL CRF',
            'uol_crf_redcap',
            'https://crf.lcbru.le.ac.uk',
            '7.2.2',
        ),
        (
            'UoL Internet',
            'uol_survey_redcap',
            'https://redcap.lcbru.le.ac.uk',
            '7.2.2',
        ),
        (
            'UoL recharge',
            'uol_recharge_redcap',
            'https://recharge.lbrc.le.ac.uk',
            '7.6.1',
        ),
        (
            'UoL eden',
            'uol_eden_redcap',
            'https://eden.lbrc.le.ac.uk/',
            '7.6.1',
        ),
    ],
)
def test__setup__redcap_instance(client, faker, instance,  database_name, base_url, version):
    create_base_data()

    iot = RedcapInstance.query.filter_by(name=instance).one_or_none()

    assert iot is not None
    assert iot.name == instance
    assert iot.database_name == database_name
    assert iot.base_url == base_url
    assert iot.version == version

