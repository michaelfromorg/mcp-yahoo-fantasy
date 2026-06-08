from .server import mcp


def main():
    """Run the Yahoo Fantasy MCP server over stdio."""
    mcp.run()


__all__ = ["main", "mcp"]
