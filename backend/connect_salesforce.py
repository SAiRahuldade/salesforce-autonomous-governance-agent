from dotenv import load_dotenv
import os
import requests

load_dotenv()


def get_env(*names):
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None

instance_url = get_env('SF_INSTANCE_URL', 'SALESFORCE_INSTANCE_URL')
access_token = get_env('SF_ACCESS_TOKEN', 'SALESFORCE_ACCESS_TOKEN')

if not instance_url or not access_token:
    raise SystemExit('SF_INSTANCE_URL and SF_ACCESS_TOKEN must be set in backend/.env')

print('Using Salesforce instance:', instance_url)
print('Testing SOQL query...')

url = f"{instance_url}/services/data/v59.0/query"
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json',
}
params = {
    'q': 'SELECT Id, Name FROM Account LIMIT 5'
}

resp = requests.get(url, headers=headers, params=params)
print('Status:', resp.status_code)
print(resp.text)
