import random
from datetime import datetime
from lbrc_flask.database import db
from .security import User
from . import Study
from lbrc_flask.security.model import AuditMixin


class IdProvider(db.Model, AuditMixin):
    id_provider_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    prefix = db.Column(db.String(10))
    type = db.Column(db.String(100))

    __mapper_args__ = {
        "polymorphic_identity": "id_provider",
        "polymorphic_on": type,
    }

    def __repr__(self):
        return f'{self.type.title()}: {self.name} ({self.prefix})'


class SequentialIdProvider(IdProvider):
    __mapper_args__ = {
        "polymorphic_identity": "sequential_id_provider",
    }

    id = db.Column(db.Integer, primary_key=True)
    id_provider_id = db.Column(db.Integer, db.ForeignKey(IdProvider.id_provider_id))
    zero_fill_size = db.Column(db.Integer)
    last_number = db.Column(db.Integer, nullable=False, default=0)

    def allocate_ids(self, count):
        start = self.last_number + 1

        self.last_number = self.last_number + count

        format_string = self.prefix or ""

        if self.zero_fill_size:
            format_string += "{:0" + str(self.zero_fill_size) + "d}"
        else:
            format_string += "{}"

        return [SequentialId(format_string.format(i)) for i in range(start, self.last_number + 1)]

    def allocate_id(self):
        return self.allocate_ids(1)[0]


class SequentialId:
    def __init__(self, id):
        self.id = id

    @property
    def barcode(self):
        return self.id


class LegacyIdProvider(IdProvider):
    __mapper_args__ = {
        "polymorphic_identity": "legacy_id_provider",
    }

    id = db.Column(db.Integer, primary_key=True)
    id_provider_id = db.Column(db.Integer, db.ForeignKey(IdProvider.id_provider_id))
    number_fixed_length = db.Column(db.Integer, nullable=False)

    def allocate_id(self):
        found = 1
        tries = 0
        prospective_id = 0

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
        )

        db.session.add(actual_id)
        
        return actual_id


    def allocate_ids(self, count):
        result = []
        for _ in range(count):
            result.append(self.allocate_id())

        return result


class LegacyId(db.Model, AuditMixin):
    id = db.Column(db.Integer, primary_key=True)
    legacy_id_provider_id = db.Column(db.Integer, db.ForeignKey(LegacyIdProvider.id))
    legacy_id_provider = db.relationship(LegacyIdProvider)
    number = db.Column(db.Integer, nullable=False)

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


class BioresourceIdProvider(IdProvider):
    __mapper_args__ = {
        "polymorphic_identity": "bioresource_id_provider",
    }

    id = db.Column(db.Integer, primary_key=True)
    id_provider_id = db.Column(db.Integer, db.ForeignKey(IdProvider.id_provider_id))

    def allocate_id(self):
        prospective_id = 0
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

    def allocate_ids(self, count):
        result = []
        for _ in range(count):
            result.append(self.allocate_id())

        return result


class BioresourceId(db.Model, AuditMixin):
    id = db.Column(db.Integer, primary_key=True)
    bioresource_id_provider_id = db.Column(db.Integer, db.ForeignKey(BioresourceIdProvider.id))
    bioresource_id_provider = db.relationship(BioresourceIdProvider)
    number = db.Column(db.Integer, nullable=False)
    check_character = db.Column(db.String(1), nullable=False)
    legacy_number = db.Column(db.Integer)

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


class PseudoRandomIdProvider(IdProvider):
    __mapper_args__ = {
        "polymorphic_identity": "pseudo_random_id_provider",
    }

    # See http://preshing.com/20121224/how-to-generate-a-sequence-of-unique-random-integers/

    _PRIME = 999983 # PRIME MOD 4 must equal 3

    id = db.Column(db.Integer, primary_key=True)
    id_provider_id = db.Column(db.Integer, db.ForeignKey(IdProvider.id_provider_id))
    id_provider = db.relationship(IdProvider)
    shorten_number = db.Column(db.Boolean, default=False, nullable=True)

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
    
    def _create_pseudo_id(self, ordinal):
        unique_code = self._create_unique_id(ordinal)
        if self.shorten_number:
            formatted_code = "{}{:0>6d}".format(self.prefix, unique_code)
        else:
            formatted_code = "{}{:0>7d}".format(self.prefix, unique_code)
        check_character = self._get_checkdigit(formatted_code)
        full_code = formatted_code + check_character

        return PseudoRandomId(
            pseudo_random_id_provider_id=self.id,
            ordinal=ordinal,
            unique_code=unique_code,
            check_character=check_character,
            full_code=full_code,
        )


    def allocate_id(self):
        previous_ordinal = db.session.query(db.func.max(PseudoRandomId.ordinal)).scalar() or 0
        result = self._create_pseudo_id(previous_ordinal + 1)
        db.session.add(result)
        db.session.flush()
        db.session.commit()

        return result

    def allocate_ids(self, count):
        # Bulk inserts objects for speed that does not populate
        # the object ID, so may cause problems if the object is
        # used later on.

        result = []
        previous_ordinal = db.session.query(db.func.max(PseudoRandomId.ordinal)).scalar() or 0

        for ordinal in range(previous_ordinal + 1, previous_ordinal + count + 1):
            result.append(self._create_pseudo_id(ordinal))

        db.session.bulk_save_objects(result)
        db.session.commit()
        
        return result

    
class PseudoRandomId(db.Model, AuditMixin):
    id = db.Column(db.Integer, primary_key=True)
    pseudo_random_id_provider_id = db.Column(db.Integer, db.ForeignKey(PseudoRandomIdProvider.id))
    pseudo_random_id_provider = db.relationship(PseudoRandomIdProvider)
    ordinal = db.Column(db.Integer, nullable=False)
    unique_code = db.Column(db.Integer, nullable=False)
    check_character = db.Column(db.String(1), nullable=False)
    full_code = db.Column(db.String(20), nullable=False)

    @property
    def barcode(self):
        return self.full_code


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
