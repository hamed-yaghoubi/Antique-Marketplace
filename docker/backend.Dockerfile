# syntax=docker/dockerfile:1
FROM python:3.14-slim

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/pip pip install uv

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv uv sync --no-dev

COPY src/ ./src/
COPY alembic.ini ./

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
