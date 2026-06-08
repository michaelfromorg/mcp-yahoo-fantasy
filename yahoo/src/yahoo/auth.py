"""
Yahoo OAuth2 for the MCP server.

Authorization is a one-time step: `uv run yahoo-login` runs Yahoo's OAuth2 flow and saves
the credentials (client id/secret + refresh token) to a `.env` file. `.env` is the source of
truth: `session()` loads it and bridges the credentials into the `oauth2.json` file
`yahoo_oauth` expects, then returns a token-refreshed `OAuth2` session that
`yahoo_fantasy_api` uses for every call. `oauth2.json` is just the derived cache
`yahoo_oauth` reads and refreshes; rebuilding it from `.env` each start means a fresh login
always takes effect. With no `.env`/env credentials, an existing `oauth2.json` (e.g. one you
placed by hand) is used as-is.
"""

import json
import logging
import os
from pathlib import Path

from yahoo_oauth import OAuth2

# yahoo_oauth logs token timing at DEBUG on every call (and installs its own stderr
# handler at import); quiet it to WARNING so server/CLI logs stay readable.
logging.getLogger("yahoo_oauth").setLevel(logging.WARNING)

CONFIG_DIR = Path(
    os.environ.get("YAHOO_MCP_CONFIG_DIR", Path.home() / ".config" / "yahoo-fantasy-mcp")
)
OAUTH_FILE = Path(os.environ.get("YAHOO_OAUTH_FILE", CONFIG_DIR / "oauth2.json"))
ENV_FILE = Path(os.environ.get("YAHOO_ENV_FILE", Path.cwd() / ".env"))


def _parse_env(text):
    """Parse KEY=value lines from `.env` text, skipping blanks and comments."""
    entries = {}
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key, value = stripped.split("=", 1)
            entries[key.strip()] = value.strip()
    return entries


def load_env_file():
    """Load `.env` into os.environ, without clobbering real env vars."""
    if ENV_FILE.is_file():
        for key, value in _parse_env(ENV_FILE.read_text()).items():
            os.environ.setdefault(key, value)


def write_env(values):
    """Merge `values` into `.env`, preserving any unrelated keys already there."""
    entries = _parse_env(ENV_FILE.read_text()) if ENV_FILE.is_file() else {}
    entries.update(values)
    ENV_FILE.write_text("".join(f"{k}={v}\n" for k, v in entries.items()))


def _bridge_env_to_oauth_file():
    """Write a fresh oauth2.json from the YAHOO_* credentials in the environment.

    Returns True if credentials were present and written, False if none are set.
    """
    key = os.environ.get("YAHOO_CONSUMER_KEY")
    secret = os.environ.get("YAHOO_CONSUMER_SECRET")
    if not (key and secret):
        return False
    payload = {
        "consumer_key": key,
        "consumer_secret": secret,
        "token_type": "bearer",
        # token_time 0 makes yahoo_oauth treat the access token as stale and refresh it on
        # first use -- the refresh token is what we persist, so the access token is derived.
        "token_time": 0,
    }
    if os.environ.get("YAHOO_ACCESS_TOKEN"):
        payload["access_token"] = os.environ["YAHOO_ACCESS_TOKEN"]
    if os.environ.get("YAHOO_REFRESH_TOKEN"):
        payload["refresh_token"] = os.environ["YAHOO_REFRESH_TOKEN"]
    OAUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    OAUTH_FILE.write_text(json.dumps(payload))
    return True


def session():
    """A ready-to-use, token-refreshed yahoo_oauth OAuth2 session."""
    load_env_file()
    if not _bridge_env_to_oauth_file() and not OAUTH_FILE.is_file():
        raise RuntimeError(
            "No Yahoo credentials found. Run `uv run yahoo-login` to authorize, or set "
            "YAHOO_CONSUMER_KEY/YAHOO_CONSUMER_SECRET (and tokens) in the environment or "
            ".env. See yahoo/README.md for setup."
        )
    sc = OAuth2(None, None, from_file=str(OAUTH_FILE))
    if not sc.token_is_valid():
        sc.refresh_access_token()
    return sc
