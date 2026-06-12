from validate_env import check_env
from services.sf_oauth import SalesforceOAuth


if not check_env():
    print('Environment not ready. Copy .env.example to .env and fill values.')
    raise SystemExit(1)


# Test OAuth
oauth = SalesforceOAuth()

try:
    print("Testing Salesforce OAuth connection...")
    token = oauth.get_access_token()
    print(f"✅ Access Token: {token[:20]}...")

    # Try a simple query
    print("\nTesting SOQL query...")
    result = oauth.query("SELECT Id, Name FROM Account LIMIT 5")
    print(f"✅ Query successful! Found {len(result.get('records', []))} accounts")

    for record in result.get('records', []):
        print(f"  - {record.get('Name')}")

except Exception as e:
    print(f"❌ Error: {e}")