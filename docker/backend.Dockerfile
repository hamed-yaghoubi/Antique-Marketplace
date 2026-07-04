FROM python:3.14-slim

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/pip pip install uv

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv uv sync --no-dev

COPY src/ ./src/
COPY alembic.ini ./
COPY docker/entrypoint.sh ./

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
