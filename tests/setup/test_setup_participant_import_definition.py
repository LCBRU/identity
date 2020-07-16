import pytest
from identity.database import db
from identity.setup.redcap_instances import REDCapInstanceDetail
from identity.model import Study
from identity.setup.studies import StudyName
from identity.redcap.model import ParticipantImportDefinition, RedcapInstance, RedcapProject
from identity.setup import create_base_data


@pytest.mark.parametrize(
    "instance, study_name, project_id",
    [
        (
            REDCapInstanceDetail.UHL_LIVE['name'],
            StudyName.ALLEVIATE,
            98,
        ),
        (
            REDCapInstanceDetail.UOL_CRF['name'],
            StudyName.ALLEVIATE,
            45,
        ),
    ],
)
def test__create_base_data__creates_alleviate_participant_import_definitions(client, faker, instance, study_name, project_id):
    ri = RedcapInstance.query.filter_by(name=instance).one_or_none()
    rp = RedcapProject(
        redcap_instance_id=ri.id,
        project_id=project_id,
    )

    db.session.add(rp)
    db.session.commit()

    create_base_data()

    s = Study.query.filter_by(name=study_name).one_or_none()

    assert ParticipantImportDefinition.query.filter_by(
        study_id=s.id,
        redcap_project_id=rp.id,
    ).one_or_none() is not None
