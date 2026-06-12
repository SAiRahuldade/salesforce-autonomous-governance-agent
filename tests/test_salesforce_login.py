"""One-off Salesforce login test supporting token-based or username/password auth."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from simple_salesforce import Salesforce
from simple_salesforce.exceptions import SalesforceAuthenticationFailed

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def get_env(*names):
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


def test_login() -> None:
    instance_url = get_env("SF_INSTANCE_URL", "SALESFORCE_INSTANCE_URL")
    access_token = get_env("SF_ACCESS_TOKEN", "SALESFORCE_ACCESS_TOKEN")

    if instance_url and access_token:
        print(f"Connecting using saved OAuth access token to {instance_url}...")
        try:
            sf = Salesforce(instance_url=instance_url, session_id=access_token)
        except SalesforceAuthenticationFailed as exc:
            print(f"FAIL: Authentication failed — {exc}")
            sys.exit(1)
    else:
        username = get_env("SF_USERNAME", "SALESFORCE_USERNAME")
        password = get_env("SF_PASSWORD", "SALESFORCE_PASSWORD")
        domain = get_env("SF_DOMAIN", "SALESFORCE_DOMAIN", "login")
        security_token = get_env("SF_SECURITY_TOKEN", "SALESFORCE_SECURITY_TOKEN", "")

        if not username or not password:
            print("FAIL: Set Salesforce credentials or access token in .env")
            sys.exit(1)

        print(f"Connecting as {username} (domain={domain})...")
        try:
            sf = Salesforce(
                username=username,
                password=password,
                security_token=security_token,
                domain=domain,
            )
        except SalesforceAuthenticationFailed as exc:
            print(f"FAIL: Authentication failed — {exc}")
            sys.exit(1)

    org_id = sf.query("SELECT Id, Name, OrganizationType FROM Organization")["records"][0]
    print("SUCCESS: Logged in to Salesforce")
    print(f"  Org name: {org_id['Name']}")
    print(f"  Org type: {org_id['OrganizationType']}")
    print(f"  Instance: {sf.sf_instance}")


if __name__ == "__main__":
    test_login()
