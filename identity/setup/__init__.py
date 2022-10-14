from lbrc_flask.database import db
from identity.model.id import ParticipantIdentifierType
from lbrc_flask.security import get_system_user

def setup_data():
    user = get_system_user()
    
    _setup_participant_identifier_types(user)

def _setup_participant_identifier_types(user):
    if ParticipantIdentifierType.query.filter_by(name=ParticipantIdentifierType.STUDY_PARTICIPANT_ID).count() > 0:
        return
    
    db.session.add(ParticipantIdentifierType(
        name=ParticipantIdentifierType.STUDY_PARTICIPANT_ID,
        last_updated_by_user_id=user.id,
    ))
    db.session.commit()