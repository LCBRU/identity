import random
from datetime import datetime
from identity.database import db
from .security import User
from . import Study


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
    
    def _create_pseudo_id(self, ordinal, user):
        unique_code = self._create_unique_id(ordinal)
        formatted_code = "{}{:0>7d}".format(self.prefix, unique_code)
        check_character = self._get_checkdigit(formatted_code)
        full_code = formatted_code + check_character

        return PseudoRandomId(
            pseudo_random_id_provider_id=self.id,
            ordinal=ordinal,
            unique_code=unique_code,
            check_character=check_character,
            full_code=full_code,
            last_updated_by_user_id=user.id,
        )


    def allocate_id(self, user):
        previous_ordinal = db.session.query(db.func.max(PseudoRandomId.ordinal)).scalar() or 0
        result = self._create_pseudo_id(previous_ordinal + 1, user)
        db.session.add(result)

        return result

    def allocate_ids(self, count, user):
        # Bulk inserts objects for speed that does not populate
        # the object ID, so may cause problems if the object is
        # used later on.

        result = []
        previous_ordinal = db.session.query(db.func.max(PseudoRandomId.ordinal)).scalar() or 0

        for ordinal in range(previous_ordinal + 1, previous_ordinal + count + 1):
            result.append(self._create_pseudo_id(ordinal, user))

        db.session.bulk_save_objects(result)
        db.session.commit()
        
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
        return FixedId(self._id)

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


class FixedId():
    def __init__(self, id):
        self._id = id

    @property
    def barcode(self):
        return self._id


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


class ParticipantIdentifierType(db.Model):

    __STUDY_PARTICIPANT_ID__ = 'study_participant_id'
    __BRICCS_ID__ = 'briccs_id'
    __PILOT_ID__ = 'pilot_id'
    __NHS_NUMBER__ = 'nhs_number'
    __UHL_SYSTEM_NUMBER__ = 'uhl_system_number'

    __TYPE_NAMES__ = [
        __STUDY_PARTICIPANT_ID__,
        __BRICCS_ID__,
        __PILOT_ID__,
        __NHS_NUMBER__,
        __UHL_SYSTEM_NUMBER__,
    ]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    def __str__(self):
        return self.name

    @staticmethod
    def get_type(type_name):
        return ParticipantIdentifierType.query.filter_by(
            name=type_name,
        ).one_or_none()

    @staticmethod
    def get_study_participant_id():
        return ParticipantIdentifierType.get_type(ParticipantIdentifierType.__STUDY_PARTICIPANT_ID__)


participant_identifiers__participant_identifier_sources = db.Table(
    'participant_identifiers__participant_identifier_sources',
    db.Column('participant_identifier_source_id', db.Integer(), db.ForeignKey('participant_identifier_source.id'), primary_key=True),
    db.Column('participant_identifier_id', db.Integer(), db.ForeignKey('participant_identifier.id'), primary_key=True),
)


class ParticipantIdentifier(db.Model):
    __tablename__ = 'participant_identifier'

    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(100), nullable=False)
    participant_identifier_type_id = db.Column(db.Integer, db.ForeignKey(ParticipantIdentifierType.id))
    participant_identifier_type = db.relationship(ParticipantIdentifierType)

    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    sources = db.relationship("ParticipantIdentifierSource", secondary=participant_identifiers__participant_identifier_sources, back_populates="identifiers", collection_class=set)

    def __str__(self):
        return f"{self.type.name}: {self.identifier}"


class ParticipantIdentifierSource(db.Model):
    __tablename__ = 'participant_identifier_source'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    study_id = db.Column(db.Integer, db.ForeignKey(Study.id), nullable=True)
    study = db.relationship(Study, backref=db.backref("participant_identifier_sources"))

    __mapper_args__ = {
        'polymorphic_identity':'participant_identifier_source',
        'polymorphic_on':type,
    }

    last_updated_datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated_by_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    last_updated_by_user = db.relationship(User)

    identifiers = db.relationship("ParticipantIdentifier", secondary=participant_identifiers__participant_identifier_sources, back_populates="sources", collection_class=set)

    def __str__(self):
        return f"{self.type.name}: {self.identifier}"


class LabelParticipantIdentifierSource(ParticipantIdentifierSource):
    __tablename__ = 'label_participant_identifier_source'

    id = db.Column(db.Integer, db.ForeignKey('participant_identifier_source.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'label_participant_identifier_source',
    }
