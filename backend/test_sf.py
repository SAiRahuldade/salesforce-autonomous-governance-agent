from simple_salesforce import Salesforce
from dotenv import load_dotenv
import os

load_dotenv()

print("Connecting to Salesforce...")

def get_env(*names):
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None

instance_url = get_env('SF_INSTANCE_URL', 'SALESFORCE_INSTANCE_URL')
access_token = get_env('SF_ACCESS_TOKEN', 'SALESFORCE_ACCESS_TOKEN')

if instance_url and access_token:
    print('Using saved OAuth access token from environment.')
    sf = Salesforce(instance_url=instance_url, session_id=access_token)
else:
    sf = Salesforce(
        username=get_env('SF_USERNAME', 'SALESFORCE_USERNAME'),
        password=get_env('SF_PASSWORD', 'SALESFORCE_PASSWORD'),
        security_token=get_env('SF_SECURITY_TOKEN', 'SALESFORCE_SECURITY_TOKEN'),
        domain=get_env('SF_DOMAIN', 'SALESFORCE_DOMAIN', 'login')
    )

result = sf.query("SELECT Id, Name FROM Account LIMIT 5")

print("✅ Connected successfully!")
print(result["records"])