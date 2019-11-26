#!/usr/bin/env python3

from dotenv import load_dotenv

# Load environment variables from '.env' file.
load_dotenv()

from identity import create_app

application = create_app()
