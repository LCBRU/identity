import ldap
import random
import sqlalchemy
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from flask import current_app
from flask_login import UserMixin
from .database import db
from identity.utils import log_exception


users_studies = db.Table(
    'users_studies',
    db.Column(
        'user_id',
        db.Integer(),
        db.ForeignKey('user.id'),
        primary_key=True,
    ),
    db.Column(
        'study_id',
        db.Integer(),
        db.ForeignKey('study.id'),
        primary_key=True,
    ),
)


roles_users = db.Table(
    'roles_users',
    db.Column(
        'user_id',
        db.Integer(),
        db.ForeignKey('user.id'),
    ),
    db.Column(
        'role_id',
        db.Integer(),
        db.ForeignKey('role.id'),
    ),
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    active = db.Column(db.Boolean, default=True)
    created_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    studies = db.relationship(
        "Study", secondary=users_studies, collection_class=set, backref=db.backref("users", lazy="dynamic")
    )
    roles = db.relationship(
        "Role", secondary=roles_users, collection_class=set, backref=db.backref("users", lazy="dynamic")
    )

    @property
    def is_active(self):
        return self.active

    @property
    def is_admin(self):
        return Role.ADMIN_ROLENAME in [r.name for r in self.roles]

    @property
    def full_name(self):
        user = self._search_ldap()

        return f"{user['given_name']} {user['surname']}".strip()

    @property
    def email(self):
        user = self._search_ldap()
        return user['email']

    def __str__(self):
        return self.email or self.username

    def _search_ldap(self):
        if current_app.config['TESTING']:
            return {
                'username': self.username,
                'email': '',
                'name': '',
                'surname': '',
                'given_name': '',
            }

        l = ldap.initialize(current_app.config['LDAP_URI'])
        l.protocol_version = 3
        l.set_option(ldap.OPT_REFERRALS, 0)

        try:
            l.simple_bind_s(
                current_app.config['LDAP_USER'],
                current_app.config['LDAP_PASSWORD'],
            )

            search_result = l.search_s(
                'DC=xuhl-tr,DC=nhs,DC=uk',
                ldap.SCOPE_SUBTREE,
                'sAMAccountName={}'.format(self.username),
            )

        except ldap.LDAPError as e:
            log_exception(e)

        if isinstance(search_result[0][1], dict):
            user = search_result[0][1]
            return {
                'username': user['sAMAccountName'][0].decode("utf-8"),
                'email': user['mail'][0].decode("utf-8"),
                'name': user['name'][0].decode("utf-8"),
                'surname': user['sn'][0].decode("utf-8"),
                'given_name': user['givenName'][0].decode("utf-8"),
            }
        else:
            return {
                'username': self.username,
                'email': '',
                'name': '',
                'surname': self.last_name,
                'given_name': self.first_name,
            }

    def validate_password(self, password):
        l = ldap.initialize(current_app.config['LDAP_URI'])
        l.protocol_version = 3
        l.set_option(ldap.OPT_REFERRALS, 0)

        try:
            l.simple_bind_s(self.email, password)
            return True

        except ldap.LDAPError as e:
            print(e)
            return False


class Role(db.Model):
    ADMIN_ROLENAME = 'admin'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    def __str__(self):
        return self.name or ""


class SequentialIdProvider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    prefix = db.Column(db.String(10))
    zero_fill_size = db.Column(db.Integer)
    last_number = db.Column(db.Integer, nullable=False, default=0)
    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    def allocate_ids(self, count, user):
        start = self.last_number + 1

        self.last_number = self.last_number + count
        self.last_updated_by_user = user
        self.last_updated_datetime = datetime.utcnow()

        format_string = self.prefix or ""

        if self.zero_fill_size:
            format_string += "{:0" + str(self.zero_fill_size) + "d}"
        else:
            format_string += "{}"

        return [SequentialId(format_string.format(i)) for i in range(start, self.last_number + 1)]

    def allocate_id(self, user):
        return self.allocate_ids(1, user)[0]

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


class SequentialId:
    def __init__(self, id):
        self.id = id

    @property
    def barcode(self):
        return self.id


class LegacyIdProvider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    prefix = db.Column(db.String(10), nullable=False)
    number_fixed_length = db.Column(db.Integer, nullable=False)
    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)


    def allocate_id(self, user):
        found = 1
        tries = 0

        while found > 0:
            prospective_id = random.randint(1, 900000)
            tries = tries + 1

            found = LegacyId.query.filter(
                LegacyId.legacy_id_provider_id == self.id
            ).filter(
                LegacyId.number == prospective_id
            ).count()

        actual_id = LegacyId(
            legacy_id_provider=self,
            number=prospective_id,
            last_updated_by_user=user,
        )

        db.session.add(actual_id)
        
        return actual_id


    def allocate_ids(self, count, user):
        result = []
        for _ in range(count):
            result.append(self.allocate_id(user))

        return result

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


class LegacyId(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    legacy_id_provider_id = db.Column(db.Integer, db.ForeignKey(LegacyIdProvider.id))
    legacy_id_provider = db.relationship(LegacyIdProvider)
    number = db.Column(db.Integer, nullable=False)
    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def __str__(self):
        return self.prefix + self.zero_filled_number

    @property
    def barcode(self):
        return '{}{}'.format(
            self.legacy_id_provider.prefix,
            str(self.number).zfill(self.legacy_id_provider.number_fixed_length),
        )


class BioresourceIdProvider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    prefix = db.Column(db.String(10), nullable=False)
    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)


    def allocate_id(self, user):
        found = 1
        tries = 0

        while found > 0:
            prospective_id = random.randint(1000000, 9999999)
            tries = tries + 1

            found = BioresourceId.query.filter(
                BioresourceId.bioresource_id_provider_id == self.id
            ).filter(
                BioresourceId.number == prospective_id
            ).count()

        actual_id = BioresourceId(
            bioresource_id_provider=self,
            number=prospective_id,
            check_character=self._get_checkdigit(prospective_id),
            last_updated_by_user=user,
        )

        db.session.add(actual_id)
        
        return actual_id


    def validate(self, id):
        if id[:len(self.prefix)] != self.prefix:
            return False
        
        number = id[len(self.prefix):-1]

        if len(number) != 7:
            return False
        
        if id[-1:] != self._get_checkdigit(int(number)):
            return False

        return True


    def _get_checkdigit(self, id):

        return "ZABCDEFGHJKLMNPQRSTVWXY"[id % 23]

    def allocate_ids(self, count, user):
        result = []
        for _ in range(count):
            result.append(self.allocate_id(user))

        return result

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


class BioresourceId(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bioresource_id_provider_id = db.Column(db.Integer, db.ForeignKey(BioresourceIdProvider.id))
    bioresource_id_provider = db.relationship(BioresourceIdProvider)
    number = db.Column(db.Integer, nullable=False)
    check_character = db.Column(db.String(1), nullable=False)
    legacy_number = db.Column(db.Integer)
    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def __str__(self):
        return self.full_code

    @property
    def full_code(self):
        return self.bioresource_id_provider.prefix + str(self.number) + self.check_character

    @property
    def barcode(self):
        return self.full_code


class PseudoRandomIdProvider(db.Model):
    # See http://preshing.com/20121224/how-to-generate-a-sequence-of-unique-random-integers/

    _PRIME = 999983 # PRIME MOD 4 must equal 3

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    prefix = db.Column(db.String(10), nullable=False)
    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    def _permuteQPR(self, x):
        if x >= self._PRIME:
            return x  # The 5 integers out of range are mapped to themselves.
        residue = (x * x) % self._PRIME
        return residue if (x <= self._PRIME / 2) else self._PRIME - residue

    def _create_unique_id(self, x):
        first = (self._permuteQPR(x) + sum([ord(x) for x in self.prefix])) % self._PRIME
        return self._permuteQPR(first)

    def _get_id(self, n):
        uniqueId = self._create_unique_id(n)
        formattedId = "{}{:0>7d}".format(self.prefix, uniqueId)
        checkDigit = self._get_checkdigit(formattedId)
        return "{}{}".format(formattedId, checkDigit)

    def validate(self, id):
        code = id[:-1]

        if id[:len(self.prefix)] != self.prefix:
            return False
        
        if id[-1:] != self._get_checkdigit(code):
            return False

        return True


    def _get_checkdigit(self, id):

        numerified = sum([ord(x) * i for i, x in enumerate(id)])

        return "ABCDEFGHJKLMNPQRSTVWXYZ"[numerified % 23]

    def allocate_id(self, user):
        previous_ordinal = db.session.query(db.func.max(PseudoRandomId.ordinal)).scalar() or 0
        this_ordinal = previous_ordinal + 1

        unique_code = self._create_unique_id(this_ordinal)
        formatted_code = "{}{:0>7d}".format(self.prefix, unique_code)
        check_character = self._get_checkdigit(formatted_code)
        full_code = formatted_code + check_character

        new_id = PseudoRandomId(
            pseudo_random_id_provider = self,
            ordinal = this_ordinal,
            unique_code = unique_code,
            check_character = check_character,
            full_code = full_code,
            last_updated_by_user = user,
        )

        db.session.add(new_id)
        
        return new_id

    def allocate_ids(self, count, user):
        result = []
        for _ in range(count):
            result.append(self.allocate_id(user))

        return result

    
class PseudoRandomId(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pseudo_random_id_provider_id = db.Column(db.Integer, db.ForeignKey(PseudoRandomIdProvider.id))
    pseudo_random_id_provider = db.relationship(PseudoRandomIdProvider)
    ordinal = db.Column(db.Integer, nullable=False)
    unique_code = db.Column(db.Integer, nullable=False)
    check_character = db.Column(db.String(1), nullable=False)
    full_code = db.Column(db.String(20), nullable=False)
    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    @property
    def barcode(self):
        return self.full_code


class FixedIdProvider():

    def __init__(self, id):
        self._id = id

    def allocate_id(self, user):
        return self._id

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


class Study(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __str__(self):
        return self.name or ""


class StudyIdSpecification():

    def __init__(
        self,
        study_name,
        pseudo_identifier_types=None,
        bioresource_identifier_types=None,
        legacy_identifier_types=None,
        sequential_identifier_types=None,
    ):

        self.pseudo_identifier_types = pseudo_identifier_types or []
        self.bioresource_identifier_types = bioresource_identifier_types or []
        self.legacy_identifier_types = legacy_identifier_types or []
        self.sequential_identifier_types = sequential_identifier_types or []


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


class ParticipantIdentifierType(db.Model):

    __STUDY_PARTICIPANT_ID__ = 'study_participant_id'

    __TYPE_NAMES__ = [
        __STUDY_PARTICIPANT_ID__,
    ]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    def __str__(self):
        return self.name

    @staticmethod
    def get_study_participant_id():
        return ParticipantIdentifierType.query.filter_by(
            name=ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__
        ).one_or_none()


class ParticipantIdentifier(db.Model):
    __tablename__ = 'participant_identifier'

    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(100), nullable=False)
    participant_identifier_type_id = db.Column(db.Integer, db.ForeignKey(ParticipantIdentifierType.id))
    participant_identifier_type = db.relationship(ParticipantIdentifierType)
    type = db.Column(db.String(100), nullable=False)
    study_id = db.Column(db.Integer, db.ForeignKey(Study.id), nullable=True)
    study = db.relationship(Study, backref=db.backref("participant_identifiers"))

    __mapper_args__ = {
        'polymorphic_identity':'participant_identifier',
        'polymorphic_on':type,
    }

    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    def __str__(self):
        return f"{self.type.name}: {self.identifier}"


class LabelParticipantIdentifier(ParticipantIdentifier):
    id = db.Column(db.Integer, db.ForeignKey('participant_identifier.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'label_participant_identifier',
    }
