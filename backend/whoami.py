from dotenv import load_dotenv
import os

load_dotenv()

print("Username:", os.getenv("SALESFORCE_USERNAME"))
print("Domain:", os.getenv("SALESFORCE_DOMAIN"))