import os
import sys
import requests
from xml.etree import ElementTree as ET
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

username = os.getenv('SF_USERNAME')
password = os.getenv('SF_PASSWORD')
token = os.getenv('SF_SECURITY_TOKEN')
instance_url = os.getenv('SF_INSTANCE_URL')

if not all([username, password, token, instance_url]):
    raise SystemExit('Missing Salesforce credentials in environment')

soap_body = f'''<?xml version="1.0" encoding="UTF-8"?>
<env:Envelope xmlns:xsd="http://www.w3.org/2001/XMLSchema"
              xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">
  <env:Body>
    <n1:login xmlns:n1="urn:enterprise.soap.sforce.com">
      <n1:username>{username}</n1:username>
      <n1:password>{password}{token}</n1:password>
    </n1:login>
  </env:Body>
</env:Envelope>'''

login_url = f'{instance_url.rstrip("/")}/services/Soap/u/67.0'
resp = requests.post(login_url, data=soap_body, headers={'Content-Type': 'text/xml', 'SOAPAction': 'login'}, timeout=120)
print('login status:', resp.status_code)
if resp.status_code != 200:
    print(resp.text)
    raise SystemExit('SOAP login failed')

root = ET.fromstring(resp.text)
ns = {'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/', 'sf': 'urn:enterprise.soap.sforce.com'}
session_id = root.find('.//sf:sessionId', ns).text
server_url = root.find('.//sf:serverUrl', ns).text
print('session acquired')

base_url = server_url.split('/services/Soap')[0]
tooling_url = f'{base_url}/services/data/v67.0/tooling/sobjects/CustomField/'
headers = {'Authorization': f'Bearer {session_id}', 'Content-Type': 'application/json', 'Accept': 'application/json'}

fields = [
    ('Governance_Issue__c.Record_Id__c', 'Record_Id', 'Text', {'label': 'Record Id', 'length': 18}),
    ('Governance_Issue__c.Object_Type__c', 'Object_Type', 'Text', {'label': 'Object Type', 'length': 80}),
    ('Governance_Issue__c.Issue__c', 'Issue', 'TextArea', {'label': 'Issue'}),
    ('Governance_Issue__c.Field__c', 'Field', 'Text', {'label': 'Field', 'length': 80}),
    ('Governance_Issue__c.Severity__c', 'Severity', 'Text', {'label': 'Severity', 'length': 80}),
    ('Governance_Issue__c.Status__c', 'Status', 'Text', {'label': 'Status', 'length': 80}),
    ('Governance_Issue__c.Proposed_Value__c', 'Proposed_Value', 'Text', {'label': 'Proposed Value', 'length': 255}),
    ('Governance_Issue__c.Safe_to_Automate__c', 'Safe_to_Automate', 'Checkbox', {'label': 'Safe to Automate'}),
    ('Governance_Issue__c.Approval_Status__c', 'Approval_Status', 'Text', {'label': 'Approval Status', 'length': 80}),
    ('Governance_Issue__c.Approved__c', 'Approved', 'Checkbox', {'label': 'Approved'})
]

for full_name, developer_name, field_type, metadata in fields:
    payload = {
        'FullName': full_name,
        'DeveloperName': developer_name,
        'Metadata': {'type': field_type, **metadata}
    }
    r = requests.post(tooling_url, headers=headers, json=payload, timeout=120)
    print(full_name, '->', r.status_code)
    print(r.text[:1000])
    print('---')
