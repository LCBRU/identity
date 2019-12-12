import six
from flask import current_app
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport
from zeep.xsd.types.builtins import check_no_collection, DateTime
from pprint import pprint as pp
from lxml import etree

@check_no_collection
def xmlvalue(self, value):

    if isinstance(value, six.string_types):
        # Make sure the string is a valid ISO date/time
        return value

    return self._xmlvalue(value)


DateTime._xmlvalue = DateTime.xmlvalue
DateTime.xmlvalue = xmlvalue


class SmspPatient:
    def __init__(self, nhs_number, xml):
        self._nhs_number = nhs_number
        self._xml = xml

    def get_text_from_xpath(self, xpath):
        element = self.get_element_from_xpath(xpath)

        if element is not None:
            return element.text

    def get_element_from_xpath(self, xpath):
        elements = self.get_elements_from_xpath(xpath)

        if len(elements) > 0:
            return elements[0]

    def get_elements_from_xpath(self, xpath):
        return self._xml.xpath(xpath, namespaces={
            'smsp': 'smsp.emea.psg.orionhealth.com',
        })

    @property
    def nhs_number(self):
        return self._nhs_number

    @property
    def title(self):
        return self.get_text_from_xpath("smsp:name/smsp:prefix")

    @property
    def forename(self):
        return self.get_text_from_xpath("smsp:name/smsp:given[position() = 1]")

    @property
    def middlenames(self):
        return ' '.join(n.text for n in self.get_elements_from_xpath("smsp:name/smsp:given[position() != 1]") if n.text is not None)

    @property
    def lastname(self):
        return self.get_text_from_xpath("smsp:name/smsp:family")

    @property
    def name(self):
        return ' '.join([self.forename, self.lastname])

    @property
    def sex(self):
        sex = self.get_element_from_xpath("smsp:patientPerson/smsp:administrativeGenderCode/@code")

        if sex == SMSP_SEX_FEMALE:
            return 'Female'
        elif sex == SMSP_SEX_MALE:
            return 'Male'

    @property
    def postcode(self):
        return self.get_text_from_xpath("smsp:addr[@use='H']/smsp:postalCode")

    @property
    def address(self):
        return ' '.join(n.text for n in self.get_elements_from_xpath("smsp:addr[@use='H']/smsp:streetAddressLine") if n.text is not None)

    @property
    def date_of_birth(self):
        return self.get_element_from_xpath("smsp:patientPerson/smsp:birthTime/@value")

    @property
    def date_of_death(self):
        return self.get_element_from_xpath("smsp:patientPerson/smsp:deceasedTime/@value")

    @property
    def is_deceased(self):
        return self.date_of_death is not None

    @property
    def current_gp_practice_code(self):
        return self.get_element_from_xpath("smsp:patientPerson/smsp:gPPractice/smsp:locationOrganization/smsp:id/@extension")

    def get_xml(self):
        return etree.tostring(self._xml)


# Response codes for SMSP Demographics Service

_SMSP_OK = 'SMSP-0000'

# Error codes for SMSP Demographics Service

# The parameters supplied were not a match to any Service
# User record in the PDS database. Error code 1 is a
# typical example of one error code which could have
# been returned by PDS in this scenario.
_SMSP_ERR_NO_MATCH = 'DEMOG-0001'

# The parameters supplied were not able to identify a
# single match in PDS – rather multiple potential matches
# were found. Error code 7 is a typical example of one
# error code which could have been returned by PDS in this scenario.
_SMSP_ERR_MULTIPLE_MATCHES = 'DEMOG-0007'

# The NHS Number supplied as a parameter was matched with a
# record in PDS, but identified as an NHS number that has
# been superseded via a merge and is no longer a current
# valid NHS Number. However, a replacement (superseding)
# NHS number is available and is being returned. Error
# codes 17 or 44 are typical examples of two error codes
# which could have been returned by PDS in this scenario.
_SMSP_ERR_NHS_NUMBER_SUPERSEDED = 'DEMOG-0017'

# The NHS Number supplied exists on PDS but is no longer
# in use and no replacement (superseding) NHS Number is
# available. Error code 22 is a typical example of one
# error code which could have been returned by PDS
# in this scenario.
_SMSP_ERR_NHS_NUMBER_INVALID = 'DEMOG-0022'

# The NHS Number supplied exists on PDS and is still in
# use but the demographic data also supplied does not
# result in the correct degree of matching. Error code
# 40 is a typical example of one error code which could
# have been returned by PDS in this scenario.
_SMSP_ERR_NHS_NUMBER_NOT_VERIFIED = 'DEMOG-0040'

# The NHS Number supplied is not a 10 digit new style
# NHS Number. Error code 42 is a typical example of one
# error code which could have been returned by PDS in
# this scenario.
_SMSP_ERR_NHS_NUMBER_NOT_NEW_STYLE = 'DEMOG-0042'

class SmspException(Exception):
    message='Unspecified exception'
class SmspNoMatchException(SmspException):
    message = 'No match found'
class SmspMultipleMatchesException(SmspException):
    message = 'Multiple matches found'
class SmspNhsNumberSupersededException(SmspException):
    message = 'NHS number superseded'
class SmspNhsNumberInvalidException(SmspException):
    message = 'NHS number not in use'
class SmspNhsNumberNotVerifiedException(SmspException):
    message = 'NHS number does not match demographic details'
class SmspNhsNumberNotNewStyleException(SmspException):
    message = 'NHS number invalid'

_SMSP_EXCEPTIONS = {
    _SMSP_ERR_NO_MATCH: SmspNoMatchException,
    _SMSP_ERR_MULTIPLE_MATCHES: SmspMultipleMatchesException,
    _SMSP_ERR_NHS_NUMBER_SUPERSEDED: SmspNhsNumberSupersededException,
    _SMSP_ERR_NHS_NUMBER_INVALID: SmspNhsNumberInvalidException,
    _SMSP_ERR_NHS_NUMBER_NOT_VERIFIED: SmspNhsNumberNotVerifiedException,
    _SMSP_ERR_NHS_NUMBER_NOT_NEW_STYLE: SmspNhsNumberNotNewStyleException,
}

SMSP_SEX_MALE = '1'
SMSP_SEX_FEMALE = '2'


def verify_nhs_number(family_name, given_name, nhs_number, dob):

    client = _get_demographics_client()

    response = client.service.verifyNHSNumber(
        familyName=family_name,
        givenName=given_name,
        nhs_number=nhs_number,
        dob=dob,
    )

    if response.responseCode == _SMSP_OK:
        return response.isValid
    else:
        raise _SMSP_EXCEPTIONS[response.responseCode]()


def get_demographics_from_search(family_name, given_name, gender, dob, postcode):
    #
    # family_name: Full surname, at least 2 characters and wildcard (*), or blank
    # given_name: Full given name, at least 2 characters and wildcard (*), or blank
    # gender: SEX_MALE or SEX_FEMALE
    #         If gender is not given, it will try both options
    # dob: Date formatted 'YYYYMMDD'.  Should accept 'YYYYMM' and 'YYYY', but this causes an error.
    # postcode: postcode or blank
    #           if postcode is given, it will also try without the postcode if a patient isn't found

    client = _get_demographics_client()

    if gender:
        genders = [gender]
    else:
        genders = [SMSP_SEX_FEMALE, SMSP_SEX_MALE]

    if postcode:
        postcodes = [postcode, '']
    else:
        postcodes = ['']

    if given_name:
        given_names = [given_name, '']
    else:
        given_names = ['']

    for gn in given_names:
        for p in postcodes:
            for gen in genders:
                response = client.service.getPatientBySearch(
                    familyName=family_name,
                    givenName=gn,
                    gender=gen,
                    dob=dob,
                    postcode=p,
                )

            if response.responseCode == _SMSP_OK:
                return SmspPatient(response.nhsNumber, response.subject._value_1[0])

    raise _SMSP_EXCEPTIONS[response.responseCode]()


def get_demographics_from_nhs_number(nhs_number, dob):
    client = _get_demographics_client()

    response = client.service.getPatientByNHSNumber(
        nhsNumber=nhs_number,
        dob=dob,
    )

    if response.responseCode == _SMSP_OK:
        return SmspPatient(response.nhsNumber, response.subject._value_1[0])
    else:
        raise _SMSP_EXCEPTIONS[response.responseCode]()


def _get_demographics_client():
    # This web service is maintained by Joss Markham (Joss.Markham@orionhealth.com)
    session = Session()
    session.verify = False
    session.auth = HTTPBasicAuth(
        current_app.config['SMSP_USERNAME'],
        current_app.config['SMSP_PASSWORD'],
    )
    transport = Transport(session=session)
    return Client(
        current_app.config['SMSP_URL'],
        transport=transport,
    )

