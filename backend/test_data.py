from services.sf_oauth import SalesforceOAuth

try:
    oauth = SalesforceOAuth()
    oauth.get_access_token()

    # Check what objects have data
    print("=== ACCOUNTS ===")
    try:
        accounts = oauth.query("SELECT Id, Name, BillingCity, BillingCountry, Industry, Phone FROM Account LIMIT 10")
        print(f"Fetched {len(accounts.get('records', []))} accounts")
        for r in accounts.get('records', []):
            print(f"  {r['Name']} | {r.get('Industry','N/A')} | {r.get('Phone','N/A')} | {r.get('BillingCity','N/A')}")
    except Exception as e:
        print(f"Error fetching accounts: {e}")

    print("\n=== CONTACTS ===")
    try:
        contacts = oauth.query("SELECT Id, FirstName, LastName, Email, Phone FROM Contact LIMIT 10")
        print(f"Fetched {len(contacts.get('records', []))} contacts")
        for r in contacts.get('records', []):
            print(f"  {r['FirstName']} {r['LastName']} | {r.get('Email','N/A')} | {r.get('Phone','N/A')}")
    except Exception as e:
        print(f"Error fetching contacts: {e}")

    print("\n=== LEADS ===")
    try:
        leads = oauth.query("SELECT Id, FirstName, LastName, Email, Company FROM Lead LIMIT 10")
        print(f"Fetched {len(leads.get('records', []))} leads")
        for r in leads.get('records', []):
            print(f"  {r['FirstName']} {r['LastName']} | {r.get('Email','N/A')} | {r.get('Company','N/A')}")
    except Exception as e:
        print(f"Error fetching leads: {e}")

except Exception as e:
    print(f"Fatal error: {e}")
    import traceback
    traceback.print_exc()