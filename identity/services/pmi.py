import typing
import datetime
from sqlalchemy.sql import text
from identity.database import pmi_engine


class PmiData(typing.NamedTuple):
    nhs_number: str
    uhl_system_number: str
    family_name: str
    given_name: str
    gender: str
    date_of_birth: datetime.date
    date_of_death: datetime.date
    postcode: str

    def __eq__(self, other):
        return (
            self.nhs_number == other.nhs_number and
            self.uhl_system_number == other.uhl_system_number and
            self.family_name == other.family_name and
            self.given_name == other.given_name and
            self.gender == other.gender and
            self.date_of_birth == other.date_of_birth and
            self.date_of_death == other.date_of_death and
            self.postcode == other.postcode
        )

    def __ne__(self, other):
        return not self.__eq__(other)


class PmiException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__()


def get_pmi(nhs_number=None, uhl_system_number=None):

    nhs_pmi = get_pmi_from_nhs_number(nhs_number)
    uhl_pmi = get_pmi_from_uhl_system_number(uhl_system_number)

    if nhs_pmi is not None and uhl_pmi is not None:
        if nhs_pmi != uhl_pmi:
            raise PmiException(f"Participant PMI mismatch for NHS Number '{nhs_number}' and UHL System Number '{uhl_system_number}'")
        
    return nhs_pmi or uhl_pmi


def get_pmi_from_nhs_number(nhs_number):
    if not nhs_number:
        return None

    with pmi_engine() as conn:
        system_numbers = conn.execute(text("""
            SELECT
                main_pat_id as uhl_system_number
            FROM PMIS_LIVE.dbo.UHL_PMI_QUERY_BY_NHS_NUMBER(:id)
            """), id=nhs_number).fetchall()

        pmi_records = {}

        for s in system_numbers:
            p = get_pmi_from_uhl_system_number(s['uhl_system_number'])

            if p and p.uhl_system_number is not None:
                pmi_records[p.uhl_system_number] = p

        if len(pmi_records) > 1:
            raise Exception(f"More than one participant found with id='{nhs_number}' in the UHL PMI")

        if len(pmi_records.values()) == 1:
            return next(iter(pmi_records.values()))


def get_pmi_from_uhl_system_number(uhl_system_number):
    if not uhl_system_number:
        return None

    with pmi_engine() as conn:

        print(list(conn.execute(text("""
            SELECT name, database_id, create_date  
            FROM sys.databases;
            """)).fetchall()))

        pmi_records = conn.execute(text("""
            SELECT
                nhs_number,
                main_pat_id as uhl_system_number,
                last_name as family_name,
                first_name as given_name,
                gender,
                dob as date_of_birth,
                date_of_death,
                postcode
            FROM PMIS_LIVE.dbo.UHL_PMI_QUERY_BY_ID(:id)
            """), id=uhl_system_number).fetchall()


        if len(pmi_records) > 1:
            raise Exception(f"More than one participant found with id='{uhl_system_number}' in the UHL PMI")

        if len(pmi_records) == 1 and pmi_records[0]['uhl_system_number'] is not None:
            pmi_record = pmi_records[0]

            return PmiData(**pmi_record)


def _get_pmi_details_from(id, function):
    if not id:
        return None

    with pmi_engine() as conn:
        pmi_records = conn.execute(text(f"""
            SELECT
                nhs_number,
                main_pat_id as uhl_system_number,
                last_name as family_name,
                first_name as given_name,
                gender,
                dob as date_of_birth,
                date_of_death,
                postcode
            FROM PMIS_LIVE.dbo.UHL_PMI_QUERY_BY_ID(:id)
            """), id=id).fetchall()

        if len(pmi_records) > 1:
            raise Exception(f"More than one participant found with id='{id}' in the UHL PMI")

        if len(pmi_records) == 1 and pmi_records[0]['uhl_system_number'] is not None:
            pmi_record = pmi_records[0]

            return PmiData(**pmi_record)
