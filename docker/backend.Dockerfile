FROM python:3.14-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --no-dev

COPY src/ ./src/
COPY static/ ./static/
COPY alembic.ini ./
COPY migrations/ ./migrations/

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
