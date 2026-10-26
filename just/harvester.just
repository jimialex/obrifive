# Catalog harvester MCP server (FastMCP). Run: just harvester <command>

set dotenv-load := false
set working-directory := "../harvester"

# List harvester commands
default:
    @just --list harvester

# Install dependencies into harvester/.venv
install:
    uv sync

# Run the MCP server over stdio (for MCP clients)
dev:
    uv run python -m src.presentation.server

# Run the MCP server over streamable HTTP on :8300
serve port="8300":
    uv run fastmcp run src/presentation/server.py:mcp --transport http --port {{port}}

# Run tests (optional pytest paths relative to harvester/)
test *paths:
    uv run pytest {{paths}}

# Static checks without autofix
check:
    uv run ruff format --check .
    uv run ruff check .
    uv run ty check

# Autofix formatting and lint
format:
    uv run ruff format .
    uv run ruff check --fix .
