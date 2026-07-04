#!/bin/sh
set -e

echo "Running Alembic migrations..."
uv run alembic upgrade head

echo "Starting backend..."
exec uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
