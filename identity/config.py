import os
from dotenv import load_dotenv

# Load environment variables from '.env' file.
load_dotenv()


class BaseConfig(object):
    IMPORT_OLD_IDS = os.getenv("IMPORT_OLD_IDS", "True") == 'True'

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False") == 'True'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    ADMIN_EMAIL_ADDRESSES = os.environ["ADMIN_EMAIL_ADDRESSES"]
    ERROR_EMAIL_SUBJECT = "LBRC identity Error"
    MAIL_DEFAULT_SENDER = os.environ["MAIL_DEFAULT_SENDER"]
    MAIL_DEBUG = os.getenv("MAIL_DEBUG", "False") == 'True'
    MAIL_SERVER = os.environ["SMTP_SERVER"]
    LDAP_URI = os.environ["LDAP_URI"]
    LDAP_USER_SUFFIX = os.environ["LDAP_USER_SUFFIX"]
    LDAP_USER = os.environ["LDAP_USER"]
    LDAP_PASSWORD = os.environ["LDAP_PASSWORD"]
    SECRET_KEY = os.environ["SECRET_KEY"]

    PRINTER_CVRC_LAB_SAMPLE = os.environ["PRINTER_CVRC_LAB_SAMPLE"]
    PRINTER_BRU_CRF_SAMPLE = os.environ["PRINTER_BRU_CRF_SAMPLE"]
    PRINTER_BRU_CRF_BAG = os.environ["PRINTER_BRU_CRF_BAG"]
    PRINTER_LIMB = os.environ["PRINTER_LIMB"]
    PRINTER_TMF_SAMPLE = os.environ["PRINTER_TMF_SAMPLE"]
    PRINTER_TMF_BAG = os.environ["PRINTER_TMF_BAG"]
    PRINTER_ADDRESS = os.environ["PRINTER_ADDRESS"]

    ADMIN_USER_USERNAME = os.environ["ADMIN_USER_USERNAME"]
    ADMIN_USER_FIRST_NAME = os.environ["ADMIN_USER_FIRST_NAME"]
    ADMIN_USER_LAST_NAME = os.environ["ADMIN_USER_LAST_NAME"]

    LEGACY_BRICCS_ID_URI = os.environ["LEGACY_BRICCS_ID_URI"]
    LEGACY_PSEUDORANDOM_ID_URI = os.environ["LEGACY_PSEUDORANDOM_ID_URI"]

    SQLALCHEMY_DATABASE_URI = os.environ["IDENTITY_DB_URI"]
    PRINTING_SET_SLEEP=2

    FILE_UPLOAD_DIRECTORY = os.environ["FILE_UPLOAD_DIRECTORY"]

    # Celery Settings
    broker_url=os.environ["BROKER_URL"]
    result_backend=os.environ["CELERY_RESULT_BACKEND"]
    CELERY_RATE_LIMIT=os.environ["CELERY_RATE_LIMIT"]
    CELERY_REDIRECT_STDOUTS_LEVEL=os.environ["CELERY_REDIRECT_STDOUTS_LEVEL"]
    CELERY_DEFAULT_QUEUE=os.environ["CELERY_DEFAULT_QUEUE"]

    # Demographics Web Service Settings
    SMSP_USERNAME=os.environ["SMSP_USERNAME"]
    SMSP_PASSWORD=os.environ["SMSP_PASSWORD"]
    SMSP_URL=os.environ["SMSP_URL"]

    # PMI
    PMI_DB_URI=os.environ["PMI_DB_URI"]

    # REDCap Database Details
    REDCAP_USERNAME=os.environ["REDCAP_USERNAME"]
    REDCAP_PASSWORD=os.environ["REDCAP_PASSWORD"]
    REDCAP_HOST=os.environ["REDCAP_HOST"]

    # REDCap Import Schedule
    REDCAP_PROJECT_SCHEDULE_MINUTE=os.environ["REDCAP_PROJECT_SCHEDULE_MINUTE"]
    REDCAP_PROJECT_SCHEDULE_HOUR=os.environ["REDCAP_PROJECT_SCHEDULE_HOUR"]
    REDCAP_PARTICIPANTS_SCHEDULE_MINUTE=os.environ["REDCAP_PARTICIPANTS_SCHEDULE_MINUTE"]
    REDCAP_PARTICIPANTS_SCHEDULE_HOUR=os.environ["REDCAP_PARTICIPANTS_SCHEDULE_HOUR"]


class TestConfig(BaseConfig):
    """Configuration for general testing"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False
    SMTP_SERVER = None
    SQLALCHEMY_ECHO = False
    PRINTING_SET_SLEEP=0
    FILE_UPLOAD_DIRECTORY = os.path.join(BaseConfig.BASE_DIR, "tests", "file_uploads")
    broker_url=os.environ["BROKER_URL"] + '/test'


class TestConfigCRSF(TestConfig):
    WTF_CSRF_ENABLED = True
