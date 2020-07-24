#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import urllib3
import logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables from '.env' file.
load_dotenv()

from identity import create_app

application = create_app()
application.app_context().push()

application.config['SERVER_NAME'] = os.environ["CELERY_SERVER_NAME"]


from identity.celery import celery
