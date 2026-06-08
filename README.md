# MCP Yahoo Fantasy

An MCP (Model Context Protocol) server that wraps the
[Yahoo Fantasy Sports API](https://sports.yahoo.com/developer/), giving an LLM read and
write access to your fantasy leagues across NFL, NHL, NBA, and MLB: standings, rosters,
matchups, players, stats, drafts, and transactions, plus lineup changes, add/drop, waiver
claims, and trade responses.

The server lives in [`yahoo/`](yahoo/). See [`yahoo/README.md`](yahoo/README.md) for setup
(authentication, configuration, and the full tool list).

## Quick start

```bash
./scripts/setup.sh          # install dependencies into yahoo/.venv via uv
cd yahoo && uv run yahoo-login   # one-time OAuth login (paste client id/secret, then a verifier code)
```

Then point your MCP client at the server (see `yahoo/README.md`).
