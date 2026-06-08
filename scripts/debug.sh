#!/bin/bash

# Launch the MCP Inspector against the Yahoo Fantasy server.

DIR="$(cd "$(dirname "$0")/../yahoo" && pwd)"

npx @modelcontextprotocol/inspector \
    uv \
    --directory "$DIR" \
    run \
    yahoo
