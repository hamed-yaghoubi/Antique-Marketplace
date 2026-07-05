#!/bin/sh
set -e

echo "Running Alembic migrations..."
uv run alembic upgrade head

echo "Starting backend..."
# ✅ فقط این خط تغییر می‌کنه (جایگزین خط آخر)
exec uv run uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
