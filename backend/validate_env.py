from dotenv import load_dotenv
import os

load_dotenv()

REQUIRED_CREDENTIALS = [
    'SF_CLIENT_ID',
    'SF_CLIENT_SECRET',
    'SF_USERNAME',
    'SF_PASSWORD',
    'SF_SECURITY_TOKEN',
]

OPTIONAL_TOKEN = 'SF_ACCESS_TOKEN'


def get_env(*names):
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


def masked(v):
    if not v:
        return None
    if len(v) <= 6:
        return '*' * len(v)
    return v[:3] + '*' * (len(v)-6) + v[-3:]


def check_env():
    print('Checking Salesforce environment variables...')
    has_token = bool(get_env(OPTIONAL_TOKEN, 'SALESFORCE_ACCESS_TOKEN'))
    has_instance = bool(get_env('SF_INSTANCE_URL', 'SALESFORCE_INSTANCE_URL'))

    for k in REQUIRED_CREDENTIALS:
        env_val = get_env(k, k.replace('SF_', 'SALESFORCE_'))
        print(f"- {k} / {k.replace('SF_', 'SALESFORCE_')}: {'SET' if env_val else 'MISSING'}")

    print(f"- SF_ACCESS_TOKEN / SALESFORCE_ACCESS_TOKEN: {'SET' if has_token else 'MISSING'}")
    print(f"- SF_INSTANCE_URL / SALESFORCE_INSTANCE_URL: {get_env('SF_INSTANCE_URL', 'SALESFORCE_INSTANCE_URL', 'https://login.salesforce.com')}")

    if has_token and has_instance:
        print('\nAccess token path is available. No next step required for token-based auth.')
        return True

    missing = []
    for k in REQUIRED_CREDENTIALS:
        if not get_env(k, k.replace('SF_', 'SALESFORCE_')):
            missing.append(k)

    if missing:
        print('\nMissing required Salesforce credentials. Create backend/.env with:')
        for k in REQUIRED_CREDENTIALS:
            print(f"{k}=your_value_here")
        print('Or set SF_ACCESS_TOKEN and SF_INSTANCE_URL for saved token auth.')
        return False

    print('\nMasked values:')
    for k in REQUIRED_CREDENTIALS:
        print(f"- {k}: {masked(get_env(k, k.replace('SF_', 'SALESFORCE_')))}")
    print(f"- SF_ACCESS_TOKEN: {'SET' if has_token else 'MISSING'}")
    return True


if __name__ == '__main__':
    ok = check_env()
    if not ok:
        raise SystemExit(1)
