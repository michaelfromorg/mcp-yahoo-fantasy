#!/bin/bash

# Install dependencies for the Yahoo Fantasy MCP server.

set -e

cd "$(dirname "$0")/../yahoo"
uv sync

echo
echo "Dependencies installed. Next: log in to Yahoo (one time):"
echo "  cd yahoo && uv run yahoo-login --client-id <id> --client-secret <secret>"
