import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from requests.exceptions import Timeout


root_env_path = Path(__file__).resolve().parents[2] / ".env"
backend_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(root_env_path)
load_dotenv(backend_env_path, override=True)


class SalesforceOAuth:
    def __init__(self):
        self.client_id = os.getenv("SF_CLIENT_ID")
        self.client_secret = os.getenv("SF_CLIENT_SECRET")
        self.username = os.getenv("SF_USERNAME")
        self.password = os.getenv("SF_PASSWORD")
        self.security_token = os.getenv("SF_SECURITY_TOKEN")
        self.instance_url = os.getenv("SF_INSTANCE_URL", "https://login.salesforce.com")
        self.access_token = os.getenv("SF_ACCESS_TOKEN")
        self.request_timeout = int(os.getenv("SF_REQUEST_TIMEOUT", "30"))

    def get_access_token(self):
        """Get OAuth access token from Salesforce."""

        if self.access_token:
            print("Using saved access token from environment.")
            return self.access_token

        token_url = f"{self.instance_url}/services/oauth2/token"
        full_password = f"{self.password}{self.security_token}"

        payload = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": full_password,
        }

        try:
            print(f"Requesting token from {token_url}...")
            response = requests.post(token_url, data=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.instance_url = data.get("instance_url", self.instance_url)
                print("OAuth successful.")
                print(f"Instance URL: {self.instance_url}")
                return self.access_token

            try:
                err = response.json()
            except Exception:
                err = None

            print(f"OAuth failed: {response.status_code}")
            print(f"Response: {response.text}")

            if err and err.get("error") == "invalid_grant":
                guidance = (
                    "authentication failure. Check credentials, append security token "
                    "to the password, ensure the connected app allows the password grant, "
                    "and that the user is not locked or requires verification."
                )
                raise Exception(f"OAuth failed: {err}. Guidance: {guidance}")

            raise Exception(f"OAuth failed: {response.text}")

        except Exception as e:
            print(f"Error getting access token: {e}")
            raise

    def _headers(self):
        if not self.access_token:
            self.get_access_token()

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def query(self, query_string):
        """Execute SOQL query against Salesforce."""

        url = f"{self.instance_url}/services/data/v59.0/query"
        params = {"q": query_string}

        try:
            response = requests.get(
                url,
                headers=self._headers(),
                params=params,
                timeout=self.request_timeout,
            )

            if response.status_code == 200:
                return response.json()
            if response.status_code == 401:
                print("Token expired or invalid, refreshing...")
                self.access_token = None
                return self.query(query_string)

            print(f"Query failed: {response.status_code}")
            print(f"Response: {response.text}")
            raise Exception(f"Query failed: {response.text}")

        except Exception as e:
            print(f"Error querying Salesforce: {e}")
            raise

    def update_record(self, object_name, record_id, fields):
        """Update a Salesforce record."""

        url = f"{self.instance_url}/services/data/v59.0/sobjects/{object_name}/{record_id}"

        try:
            response = self._patch_with_retry(url, fields)

            if response.status_code == 204:
                return {"status": "success"}
            if response.status_code == 401:
                print("Token expired or invalid, refreshing...")
                self.access_token = None
                return self.update_record(object_name, record_id, fields)

            print(f"Update failed: {response.status_code}")
            print(f"Response: {response.text}")
            raise Exception(f"Update failed: {response.text}")

        except Exception as e:
            print(f"Error updating Salesforce record: {e}")
            raise

    def _patch_with_retry(self, url, fields):
        last_timeout = None

        for attempt in range(2):
            try:
                return requests.patch(
                    url,
                    headers=self._headers(),
                    json=fields,
                    timeout=self.request_timeout,
                )
            except Timeout as e:
                last_timeout = e
                print(f"Salesforce update timed out on attempt {attempt + 1}: {e}")

        raise Timeout(
            "Salesforce did not respond in time. Please check your internet/VPN "
            "connection and try again."
        ) from last_timeout
