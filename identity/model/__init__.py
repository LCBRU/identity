import urllib.parse
from datetime import datetime
from identity.database import db
from .security import User


class Study(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __str__(self):
        return self.name or ""


class RedcapInstance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    database_name = db.Column(db.String(100), nullable=False)
    base_url = db.Column(db.String(500), nullable=False)
    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    def __str__(self):
        return self.name


class RedcapProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    project_id = db.Column(db.Integer, nullable=False)
    redcap_instance_id = db.Column(db.Integer, db.ForeignKey(RedcapInstance.id), nullable=False)
    redcap_instance = db.relationship(RedcapInstance, backref=db.backref("projects"))
    study_id = db.Column(db.Integer, db.ForeignKey(Study.id))
    study = db.relationship(Study, backref=db.backref("redcap_projects"))
    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    def __str__(self):
        return self.name

    def get_link(self, record_id):
        return urllib.parse.urljoin(self.redcap_instance.base_url, f'DataEntry/record_home.php?pid={self.project_id}&id={record_id}')


ecrf_details__participant_identifiers = db.Table(
    'ecrf_details__participant_identifiers',
    db.Column(
        'ecrf_detail_id',
        db.Integer(),
        db.ForeignKey('ecrf_detail.id'),
        primary_key=True,
    ),
    db.Column(
        'participant_identifier_id',
        db.Integer(),
        db.ForeignKey('participant_identifier.id'),
        primary_key=True,
    ),
)


class EcrfDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, nullable=False)

    ecrf_participant_identifier = db.Column(db.String(100))
    recruitment_date = db.Column(db.Date)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    sex = db.Column(db.String(1))
    postcode = db.Column(db.String(10))
    birth_date = db.Column(db.Date)
    complete_or_expected = db.Column(db.Boolean)
    non_completion_reason = db.Column(db.String(10))
    withdrawal_date = db.Column(db.Date)
    post_withdrawal_keep_samples = db.Column(db.Boolean)
    post_withdrawal_keep_data = db.Column(db.Boolean)
    brc_opt_out = db.Column(db.Boolean)
    ecrf_timestamp = db.Column(db.BigInteger)

    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    identifiers = db.relationship(
        "ParticipantIdentifier",
        secondary=ecrf_details__participant_identifiers,
        collection_class=set,
        backref=db.backref("ecrf_details", lazy="dynamic")
    )

    def __str__(self):
        return self.ecrf_participant_identifier
