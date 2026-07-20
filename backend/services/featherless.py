import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class FeatherlessError(Exception):
    pass

def _get_api_key():
    """Fetch API key from environment at call time (safer than module load time)."""
    key = os.environ.get("FEATHERLESS_API_KEY")
    if not key:
        logger.error("FEATHERLESS_API_KEY not found in environment variables")
        raise FeatherlessError("FEATHERLESS_API_KEY not set in environment")
    return key

def _get_base_url():
    """Fetch base URL from environment, default to placeholder."""
    return os.environ.get("FEATHERLESS_BASE_URL", "https://api.featherless.example")

def _auth_headers():
    key = _get_api_key()
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

def generate_text(prompt: str, model: str = "default", timeout: int = 30, **kwargs):
    """Call Featherless text generation endpoint.

    This function reads the API key from the environment at call time and does not store secrets.
    """
    url = f"{_get_base_url().rstrip('/')}/v1/generate"
    payload = {"model": model, "prompt": prompt}
    payload.update(kwargs)
    try:
        resp = requests.post(url, json=payload, headers=_auth_headers(), timeout=timeout)
        resp.raise_for_status()
    except requests.HTTPError as e:
        error_msg = f"Featherless API error: {e} - {resp.text}"
        logger.error(error_msg)
        raise FeatherlessError(error_msg)
    except Exception as e:
        error_msg = f"Featherless request failed: {e}"
        logger.error(error_msg)
        raise FeatherlessError(error_msg)
    return resp.json()

# Example (do not run with a hard-coded key):
# from backend.services.featherless import generate_text
# print(generate_text("Hello from Featherless"))
