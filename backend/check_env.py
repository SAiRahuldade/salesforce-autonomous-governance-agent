# backend/check_env.py

from dotenv import load_dotenv
import os

load_dotenv()

print("USERNAME loaded:", bool(os.getenv("SALESFORCE_USERNAME")))
print("PASSWORD loaded:", bool(os.getenv("SALESFORCE_PASSWORD")))
print("TOKEN loaded:", bool(os.getenv("SALESFORCE_SECURITY_TOKEN")))
print("DOMAIN:", os.getenv("SALESFORCE_DOMAIN"))