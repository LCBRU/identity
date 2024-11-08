import os
from lbrc_flask.config import BaseConfig, BaseTestConfig


class IdentityConfig():
    IMPORT_OLD_IDS = os.getenv("IMPORT_OLD_IDS", "True") == 'True'

    PRINTER_DEV = os.environ["PRINTER_DEV"]
    PRINTER_CVRC_LAB_SAMPLE = os.environ["PRINTER_CVRC_LAB_SAMPLE"]
    PRINTER_BRU_CRF_SAMPLE = os.environ["PRINTER_BRU_CRF_SAMPLE"]
    PRINTER_BRU_CRF_BAG = os.environ["PRINTER_BRU_CRF_BAG"]
    PRINTER_LIMB = os.environ["PRINTER_LIMB"]
    PRINTER_TMF_SAMPLE = os.environ["PRINTER_TMF_SAMPLE"]
    PRINTER_TMF_BAG = os.environ["PRINTER_TMF_BAG"]
    PRINTER_ADDRESS = os.environ["PRINTER_ADDRESS"]

    PRINTING_SET_SLEEP = 3

    FILE_UPLOAD_DIRECTORY = os.environ["FILE_UPLOAD_DIRECTORY"]

    # Celery Settings
    BROKER_URL=os.environ["BROKER_URL"]
    CELERY_RESULT_BACKEND=os.environ["CELERY_RESULT_BACKEND"]
    CELERY_RATE_LIMIT=os.environ["CELERY_RATE_LIMIT"]
    CELERY_REDIRECT_STDOUTS_LEVEL=os.environ["CELERY_REDIRECT_STDOUTS_LEVEL"]
    CELERY_DEFAULT_QUEUE=os.environ["CELERY_DEFAULT_QUEUE"]

    # Demographics Web Service Settings
    SMSP_USERNAME=os.environ["SMSP_USERNAME"]
    SMSP_PASSWORD=os.environ["SMSP_PASSWORD"]
    SMSP_URL=os.environ["SMSP_URL"]

    # PMI
    PMI_DB_URI=os.environ["PMI_DB_URI"]

    # CiviCRM
    CIVICRM_DB_URI=os.environ["CIVICRM_DB_URI"]

    # REDCap Database Details
    REDCAP_USERNAME=os.environ["REDCAP_USERNAME"]
    REDCAP_PASSWORD=os.environ["REDCAP_PASSWORD"]
    REDCAP_HOST=os.environ["REDCAP_HOST"]

    # REDCap Import Schedule
    REDCAP_PROJECT_SCHEDULE_MINUTE=os.environ["REDCAP_PROJECT_SCHEDULE_MINUTE"]
    REDCAP_PROJECT_SCHEDULE_HOUR=os.environ["REDCAP_PROJECT_SCHEDULE_HOUR"]
    REDCAP_PARTICIPANTS_SCHEDULE_MINUTE=os.environ["REDCAP_PARTICIPANTS_SCHEDULE_MINUTE"]
    REDCAP_PARTICIPANTS_SCHEDULE_HOUR=os.environ["REDCAP_PARTICIPANTS_SCHEDULE_HOUR"]

    SQLALCHEMY_BINDS = {
        'etl_central': os.environ["ETL_CENTRAL_DB_URI"],
        'civicrm': os.environ["CIVICRM_DB_URI"],
    }


class Config(BaseConfig, IdentityConfig):
    pass


class TestConfig(BaseTestConfig):
    """Configuration for general testing"""

    PRINTING_SET_SLEEP=0
    FILE_UPLOAD_DIRECTORY = '/home/richard/tbd/identity/tests/file_uploads'
    BROKER_URL=os.environ["BROKER_URL"] + '/test'
    # PMI
    PMI_DB_URI=os.environ["PMI_DB_URI"]


class TestConfigCRSF(TestConfig):
    WTF_CSRF_ENABLED = True
