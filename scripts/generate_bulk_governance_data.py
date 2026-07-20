import os
import random
import sys
from pathlib import Path

from dotenv import load_dotenv

try:
    from simple_salesforce import Salesforce
except ImportError as exc:
    raise SystemExit("Install simple-salesforce to run this script: pip install simple-salesforce") from exc

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

SF_USERNAME = os.getenv("SF_USERNAME")
SF_PASSWORD = os.getenv("SF_PASSWORD")
SF_SECURITY_TOKEN = os.getenv("SF_SECURITY_TOKEN")
SF_INSTANCE_URL = os.getenv("SF_INSTANCE_URL")

if not all([SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN, SF_INSTANCE_URL]):
    raise SystemExit("Set SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN, and SF_INSTANCE_URL in .env")

sf = Salesforce(
    username=SF_USERNAME,
    password=SF_PASSWORD,
    security_token=SF_SECURITY_TOKEN,
    instance_url=SF_INSTANCE_URL,
    domain="login",
)

random.seed(7)


def make_account(index):
    return {
        "Name": f"Acme {index} {random.choice(['LLC', 'Inc', 'Group'])}",
        "Industry": random.choice(["Technology", "Manufacturing", "Retail", "Healthcare"]),
        "Phone": random.choice(["555-0100", "555-0101", "", "bad-phone"]),
        "BillingCity": random.choice(["Seattle", "Austin", "", "Chicago"]),
    }


def make_contact(index, account_id):
    email = random.choice([
        f"person{index}@example.com",
        f"person{index}@gmail.com",
        "",
        f"bad-email-{index}",
    ])
    return {
        "FirstName": f"Person{index}",
        "LastName": random.choice(["Smith", "Nguyen", "Patel", "Garcia"]),
        "Email": email,
        "Phone": random.choice(["555-0200", "555-0201", "", "bad-phone"]),
        "AccountId": account_id,
    }


if __name__ == "__main__":
    account_records = [make_account(i) for i in range(5000)]
    accounts = sf.bulk.Account.insert(account_records, batch_size=200)
    account_ids = [a["id"] for a in accounts if isinstance(a, dict) and a.get("success")]

    contacts = []
    for i, account_id in enumerate(account_ids):
        contacts.append(make_contact(i, account_id))
        if len(contacts) >= 5000:
            break

    sf.bulk.Contact.insert(contacts, batch_size=200)
    print(f"Inserted {len(account_ids)} accounts and {len(contacts)} contacts")
