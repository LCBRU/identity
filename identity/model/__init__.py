from datetime import datetime
from identity.database import db
from identity.model.security import User


class Study(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __str__(self):
        return self.name or ""


# study_participant__participant_identifiers = db.Table(
#     'study_participant__participant_identifiers',
#     db.Column(
#         'study_participant_id',
#         db.Integer(),
#         db.ForeignKey('study_participant.id'),
#         primary_key=True,
#     ),
#     db.Column(
#         'participant_identifier_id',
#         db.Integer(),
#         db.ForeignKey('participant_identifier.id'),
#         primary_key=True,
#     ),
# )


study_participant__participant_identifiers = db.Table(
    'study_participant__participant_identifiers',
    db.Column('study_participant_id', db.Integer(), primary_key=True),
    db.Column('participant_identifier_id', db.Integer(), primary_key=True),
    db.Column('study_id', db.Integer(), primary_key=True),
    db.ForeignKeyConstraint(
        ['study_participant_id', 'study_id'],
        ['study_participant.id', 'study_participant.study_id'],       
    ),
    db.ForeignKeyConstraint(
        ['participant_identifier_id', 'study_id'],
        ['participant_identifier.id', 'participant_identifier.study_id'],       
    ),
)


class StudyParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    study_id = db.Column(db.Integer, db.ForeignKey(Study.id), nullable=False)
    study = db.relationship(Study, backref=db.backref("participants"))

    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    participant_identifiers = db.relationship(
        "ParticipantIdentifier",
        secondary=study_participant__participant_identifiers,
        uselist=False,
        backref=db.backref('study_participant', uselist=False),
    )

