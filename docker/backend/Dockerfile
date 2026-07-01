# syntax=docker/dockerfile:1

# =============================================================================
# Backend Dockerfile - Antique Marketplace API
# =============================================================================
# Multi-stage build for optimal image size
# Stage 1: Build dependencies
# Stage 2: Production runtime

# --- Stage 1: Build ---
FROM python:3.14-slim AS builder

WORKDIR /app

# Install system dependencies for psycopg and argon2
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install Python dependencies using uv
RUN pip install --no-cache-dir uv && \
    uv sync --frozen --no-dev

# --- Stage 2: Production ---
FROM python:3.14-slim AS production

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Create non-root user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Create static directory
RUN mkdir -p /app/static/products && \
    chown -R appuser:appuser /app

# Copy application code
COPY src/ ./src/
COPY alembic.ini ./
COPY migrations/ ./migrations/

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')" || exit 1

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]

# --- Stage 3: Development ---
FROM python:3.14-slim AS development

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv and Python dependencies
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install all dependencies (including dev)
RUN uv sync

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Create static directory
RUN mkdir -p /app/static/products

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run migrations and start server with hot-reload
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"]
