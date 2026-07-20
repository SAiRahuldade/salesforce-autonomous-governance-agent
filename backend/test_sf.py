"""One-off Salesforce integration smoke test.

This file is intentionally NOT meant to run during normal `pytest` runs.
It will only execute when `RUN_LIVE_SF_TESTS=1` is set.

To run:
  set RUN_LIVE_SF_TESTS=1
  pytest -q

Or run manually:
  python backend/test_sf.py
"""

import os

import pytest
from dotenv import load_dotenv
from simple_salesforce import Salesforce

load_dotenv()


def _get_env(*names):
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


if os.getenv("RUN_LIVE_SF_TESTS", "0") != "1":
    pytest.skip("Skipping live Salesforce tests (set RUN_LIVE_SF_TESTS=1 to enable).", allow_module_level=True)


def _run_smoke_test():
    print("Connecting to Salesforce...")

    instance_url = _get_env("SF_INSTANCE_URL", "SALESFORCE_INSTANCE_URL")
    access_token = _get_env("SF_ACCESS_TOKEN", "SALESFORCE_ACCESS_TOKEN")

    if instance_url and access_token:
        print("Using saved OAuth access token from environment.")
        sf = Salesforce(instance_url=instance_url, session_id=access_token)
    else:
        sf = Salesforce(
            username=_get_env("SF_USERNAME", "SALESFORCE_USERNAME"),
            password=_get_env("SF_PASSWORD", "SALESFORCE_PASSWORD"),
            security_token=_get_env(
                "SF_SECURITY_TOKEN", "SALESFORCE_SECURITY_TOKEN"
            ),
            domain=_get_env("SF_DOMAIN", "SALESFORCE_DOMAIN", "login"),
        )

    result = sf.query("SELECT Id, Name FROM Account LIMIT 5")
    print("✅ Connected successfully!")
    print(result["records"])


if __name__ == "__main__":
    _run_smoke_test()

