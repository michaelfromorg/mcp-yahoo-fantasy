"""
One-time Yahoo authorization for the MCP server.

Runs Yahoo's OAuth2 flow through `yahoo_oauth` (the same library the server uses to refresh
tokens) and saves the resulting credentials to `.env`, which the server loads on startup.
The flow is out-of-band: open the printed URL, approve access, and Yahoo shows a verifier
code that you paste back here.

    uv run yahoo-login --client-id <id> --client-secret <secret>

Client id/secret come from your Yahoo app at https://developer.yahoo.com/apps/. They fall
back to $YAHOO_CONSUMER_KEY/$YAHOO_CONSUMER_SECRET, then to whatever is already in `.env`,
then to an interactive prompt.
"""

import argparse
import getpass
import os

from yahoo_oauth import OAuth2

from .auth import ENV_FILE, load_env_file, write_env


def main():
    parser = argparse.ArgumentParser(
        prog="yahoo-login", description="Authorize the Yahoo Fantasy MCP server."
    )
    parser.add_argument("--client-id", help="Yahoo app Client ID (Consumer Key).")
    parser.add_argument("--client-secret", help="Yahoo app Client Secret (Consumer Secret).")
    args = parser.parse_args()

    load_env_file()
    client_id = (
        args.client_id
        or os.environ.get("YAHOO_CONSUMER_KEY")
        or input("Yahoo Client ID: ").strip()
    )
    client_secret = (
        args.client_secret
        or os.environ.get("YAHOO_CONSUMER_SECRET")
        or getpass.getpass("Yahoo Client Secret: ").strip()
    )

    # browser_callback=False prints the authorization URL in the prompt (robust on headless
    # / WSL where auto-opening a browser silently fails) and reads the verifier code. The
    # OAuth2 constructor runs the whole exchange; store_file=False stops it writing its own
    # secrets.json -- we persist to .env instead.
    print("Open this URL, approve access, then paste the verifier code Yahoo shows you.\n")
    oauth = OAuth2(client_id, client_secret, browser_callback=False, store_file=False)

    write_env(
        {
            "YAHOO_CONSUMER_KEY": client_id,
            "YAHOO_CONSUMER_SECRET": client_secret,
            "YAHOO_ACCESS_TOKEN": oauth.access_token,
            "YAHOO_REFRESH_TOKEN": oauth.refresh_token,
        }
    )
    # The server rebuilds oauth2.json from .env on startup, so a fresh login just works.
    print(f"\nSaved Yahoo credentials to {ENV_FILE}. Start the server with: uv run yahoo")
