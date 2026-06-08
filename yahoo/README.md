# MCP Yahoo Fantasy

An MCP server for Yahoo Fantasy Sports. It wraps
[`yahoo_fantasy_api`](https://github.com/spilchen/yahoo_fantasy_api) and exposes its reads
and writes as MCP tools, working across NFL, NHL, NBA, and MLB.

## How it works

- **Data**: all tools call `yahoo_fantasy_api`, which returns plain JSON the model consumes
  directly.
- **Auth**: Yahoo uses three-legged OAuth2. You authorize once with `uv run yahoo-login`,
  which saves your credentials (one Yahoo app, one long-lived refresh token) to a `.env`
  file. The server loads `.env` on startup and bridges those credentials into the
  `oauth2.json` that `yahoo_fantasy_api` reads. The access token is refreshed automatically,
  so the server runs unattended after the one-time login.

## Setup

1. **Register a Yahoo app** at <https://developer.yahoo.com/apps/create/>.
   - Set the application to **Confidential Client** with **Fantasy Sports: Read/Write**
     permission.
   - Set the redirect URI to `https://localhost:8000`.
   - Note the **Client ID** (consumer key) and **Client Secret** (consumer secret).

2. **Install dependencies** (from the repo root): `./scripts/setup.sh`, or from here:

   ```bash
   uv sync
   ```

3. **Log in once** to mint a refresh token:

   ```bash
   uv run yahoo-login --client-id <id> --client-secret <secret>
   ```

   (Flags are optional -- without them you'll be prompted, or they're read from `.env`.)
   Open the printed URL, approve access, and paste back the verifier code Yahoo shows you.
   This writes your credentials to `.env` in the current directory. Run the server from that
   same directory, or point `YAHOO_ENV_FILE` at the file (see below).

   On first use the server reads `.env` and writes a refreshed
   `~/.config/yahoo-fantasy-mcp/oauth2.json`; subsequent runs reuse and auto-refresh it.

## Configuration (environment variables)

All are optional:

| Variable | Purpose |
| --- | --- |
| `YAHOO_LEAGUE_KEY` | Default league key (e.g. `449.l.365083`) so tools can omit `league_key`. Find it with the `list_leagues` tool. |
| `YAHOO_ENV_FILE` | Path to the `.env` written by `yahoo-login`, if the server doesn't run from the directory it was created in (default `./.env`). |
| `YAHOO_OAUTH_FILE` | Path to the bridged `oauth2.json` (default `~/.config/yahoo-fantasy-mcp/oauth2.json`). |
| `YAHOO_MCP_CONFIG_DIR` | Directory for the default `oauth2.json` location. |
| `YAHOO_CONSUMER_KEY` / `YAHOO_CONSUMER_SECRET` / `YAHOO_ACCESS_TOKEN` / `YAHOO_REFRESH_TOKEN` | The credentials `yahoo-login` writes to `.env`; set them directly instead if you prefer (e.g. in your MCP client config). |

## Connecting an MCP client

Add the server to your client config (e.g. Claude Desktop's `claude_desktop_config.json`),
using an absolute path:

```jsonc
{
  "mcpServers": {
    "yahoo": {
      "command": "uv",
      "args": ["--directory", "/ABSOLUTE/PATH/TO/mcp-yahoo-fantasy/yahoo", "run", "yahoo"],
      "env": {
        "YAHOO_LEAGUE_KEY": "449.l.365083",
        "YAHOO_ENV_FILE": "/ABSOLUTE/PATH/TO/.env"
      }
    }
  }
}
```

Debug interactively with the MCP Inspector: `../scripts/debug.sh` (run from this directory).

## Tools

League reads: `list_leagues`, `league_settings`, `league_standings`, `league_teams`,
`league_matchups`, `league_draft_results`, `league_transactions`, `league_stat_categories`,
`league_roster_positions`, `current_week`.

Player reads: `free_agents`, `waivers`, `taken_players`, `player_details`, `player_stats`,
`percent_owned`.

Team reads: `my_team_key`, `team_details`, `team_roster`, `team_matchup_opponent`,
`proposed_trades`.

Writes: `set_lineup`, `add_player`, `drop_player`, `add_and_drop_players`, `claim_player`,
`claim_and_drop_players`, `accept_trade`, `reject_trade`.

Most tools accept an optional `league_key`/`team_key`; without them they fall back to
`YAHOO_LEAGUE_KEY` and to your own team in that league.

> Note: proposing trades is intentionally omitted -- `yahoo_fantasy_api`'s `propose_trade`
> is broken upstream (its argument handling is inconsistent with its own helper). Accepting
> and rejecting trades works.
