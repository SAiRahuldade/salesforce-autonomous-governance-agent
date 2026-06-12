"""Simple Flask app to perform Salesforce OAuth Web Server Flow.

Usage:
1. Copy `backend/.env.example` to `backend/.env` and set `SF_CLIENT_ID`, `SF_CLIENT_SECRET`, and `SF_INSTANCE_URL`.
2. Set the connected app callback URL to http://localhost:5000/callback
3. Run: `python backend/oauth_server.py`
4. Visit http://localhost:5000/ and click 'Authorize' to log in and grant access.

After successful auth the access token will be displayed and saved to backend/.env as SF_ACCESS_TOKEN.
"""

from flask import Flask, redirect, request, url_for, session
import os
import requests
import hashlib
import base64
import secrets
from dotenv import load_dotenv
from urllib.parse import urlencode

load_dotenv()

app = Flask(__name__)
# session secret for PKCE verifier storage
# Use a stable default so the verifier survives debug reloads.
app.secret_key = os.getenv('FLASK_SECRET', 'dev-super-secret-pkce-key')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

CLIENT_ID = os.getenv('SF_CLIENT_ID')
CLIENT_SECRET = os.getenv('SF_CLIENT_SECRET')
INSTANCE = os.getenv('SF_INSTANCE_URL', 'https://login.salesforce.com')
# Allow overriding redirect URI and port via environment for flexibility
REDIRECT_URI = os.getenv('SF_REDIRECT_URI', 'http://localhost:5000/callback')
PORT = int(os.getenv('SF_PORT', '5000'))

AUTH_URL = f"{INSTANCE}/services/oauth2/authorize"
TOKEN_URL = f"{INSTANCE}/services/oauth2/token"


@app.route('/')
def index():
    if not CLIENT_ID or not CLIENT_SECRET:
        return ('Missing SF_CLIENT_ID or SF_CLIENT_SECRET in backend/.env.\n'
                'Copy backend/.env.example to backend/.env and fill values.'), 400

    # Generate PKCE code_verifier and code_challenge (S256)
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    session['code_verifier'] = code_verifier

    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
    }
    auth_full = AUTH_URL + '?' + urlencode(params)
    return f'<h3>Salesforce OAuth</h3><p><a href="{auth_full}">Authorize</a></p>'


@app.route('/callback')
def callback():
    error = request.args.get('error')
    if error:
        return f'Error: {error} - {request.args.get("error_description")}'

    code = request.args.get('code')
    if not code:
        return 'Missing code in callback', 400

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
    }

    # include code_verifier for PKCE
    code_verifier = session.get('code_verifier')
    if not code_verifier:
        return ('Failed to exchange token: missing code verifier in session. ' 
                'Make sure you access the app using the same host (http://localhost:8000) ' 
                'and refresh the page before authorizing.'), 400

    data['code_verifier'] = code_verifier

    resp = requests.post(TOKEN_URL, data=data)
    try:
        payload = resp.json()
    except Exception:
        return f'Unexpected token response: {resp.text}', 500

    if resp.status_code != 200:
        return f'Failed to exchange token: {payload}', 400

    access_token = payload.get('access_token')
    instance_url = payload.get('instance_url', INSTANCE)

    # Persist token to .env (append)
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    with open(env_path, 'a') as f:
        f.write(f"\nSF_ACCESS_TOKEN={access_token}\n")
        f.write(f"SF_INSTANCE_URL={instance_url}\n")

    return (f'<h3>Success</h3>'
            f'<p>Access Token (first 40 chars): {access_token[:40]}...</p>'
            f'<p>Saved to backend/.env as SF_ACCESS_TOKEN.</p>')


if __name__ == '__main__':
    # bind to all interfaces for localhost access and use configured port
    app.run(debug=True, host='0.0.0.0', port=PORT)
