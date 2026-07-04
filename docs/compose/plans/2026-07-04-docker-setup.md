# Docker Development Environment Implementation Plan

> [!NOTE]
> This document may not reflect the current implementation.
> See the final report for up-to-date state:
> [Final Report](../reports/docker-setup.md)

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a Docker Compose development environment with PostgreSQL, FastAPI backend (hot-reload + auto-migrations), and React/Vite frontend (hot-reload).

**Architecture:** Three services in a single docker-compose.yml: postgres (data persistence via named volume), backend (Python 3.14-slim with uv, entrypoint runs alembic then uvicorn --reload), frontend (Node 20-slim with Vite dev server). Source directories mounted as volumes for hot-reload.

**Tech Stack:** Docker, Docker Compose, Python 3.14, uv, FastAPI, Alembic, PostgreSQL 16, Node.js 20, Vite

## Global Constraints

- Python version: 3.14 (matching `.python-version`)
- Node version: 20 LTS
- PostgreSQL version: 16
- Package manager: uv (backend), npm (frontend)
- Backend runs at port 8000, Frontend at 5173, Postgres at 5432
- All Docker files go in `docker/` directory

---

## File Structure

| File | Responsibility |
|------|---------------|
| `docker/.env.docker` | Environment variables for all services |
| `docker/backend.Dockerfile` | Backend container image build |
| `docker/frontend.Dockerfile` | Frontend container image build |
| `docker/docker-compose.yml` | Service orchestration |
| `docker/entrypoint.sh` | Backend startup script (migrations + server) |
| `docker/nginx.conf` | (Not used - user chose no Nginx) |

---

### Task 1: Create Environment Configuration

**Covers:** Environment setup for all services

**Files:**
- Create: `docker/.env.docker`

- [ ] **Step 1: Create .env.docker with all required variables**

```bash
# docker/.env.docker

# PostgreSQL
POSTGRES_USER=antique_user
POSTGRES_PASSWORD=antique_pass
POSTGRES_DB=antique_marketplace

# Backend
SQLALCHEMY_DATABASE_URL=postgresql://antique_user:antique_pass@postgres:5432/antique_marketplace
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
REFRESH_TOKEN_COOKIE_NAME=refresh_token
COOKIE_PATH=/
COOKIE_MAX_AGE=604800
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
UPLOAD_DIR=static/products
ALLOWED_IMAGE_EXTENSIONS=.jpg,.jpeg,.png,.webp
MAX_IMAGE_SIZE=5242880
CORS_ORIGINS=http://localhost:5173

# Frontend
VITE_API_BASE_URL=http://localhost:8000
```

- [ ] **Step 2: Commit**

```bash
git add docker/.env.docker
git commit -m "feat: add Docker environment configuration"
```

---

### Task 2: Create Backend Dockerfile

**Covers:** Backend containerization

**Files:**
- Create: `docker/backend.Dockerfile`
- Create: `docker/entrypoint.sh`

- [ ] **Step 1: Create backend.Dockerfile**

```dockerfile
# docker/backend.Dockerfile
FROM python:3.14-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --no-dev

# Copy application code
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini ./

# Create static directory
RUN mkdir -p static/products

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
```

- [ ] **Step 2: Create entrypoint.sh**

```bash
#!/bin/bash
set -e

echo "Running database migrations..."
uv run alembic upgrade head

echo "Starting backend server..."
exec uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

- [ ] **Step 3: Commit**

```bash
git add docker/backend.Dockerfile docker/entrypoint.sh
git commit -m "feat: add backend Dockerfile with auto-migration"
```

---

### Task 3: Create Frontend Dockerfile

**Covers:** Frontend containerization

**Files:**
- Create: `docker/frontend.Dockerfile`

- [ ] **Step 1: Create frontend.Dockerfile**

```dockerfile
# docker/frontend.Dockerfile
FROM node:20-slim

WORKDIR /app

# Copy package files first for caching
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY frontend/ .

EXPOSE 5173

# Run Vite dev server, accessible from outside container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

- [ ] **Step 2: Commit**

```bash
git add docker/frontend.Dockerfile
git commit -m "feat: add frontend Dockerfile with Vite dev server"
```

---

### Task 4: Create Docker Compose File

**Covers:** Service orchestration

**Files:**
- Create: `docker/docker-compose.yml`

- [ ] **Step 1: Create docker-compose.yml**

```yaml
# docker/docker-compose.yml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ..
      dockerfile: docker/backend.Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ../src:/app/src
      - ../migrations:/app/migrations
      - ../static:/app/static
    environment:
      SQLALCHEMY_DATABASE_URL: ${SQLALCHEMY_DATABASE_URL}
      SECRET_KEY: ${SECRET_KEY}
      ALGORITHM: ${ALGORITHM}
      ACCESS_TOKEN_EXPIRE_MINUTES: ${ACCESS_TOKEN_EXPIRE_MINUTES}
      REFRESH_TOKEN_EXPIRE_DAYS: ${REFRESH_TOKEN_EXPIRE_DAYS}
      REFRESH_TOKEN_COOKIE_NAME: ${REFRESH_TOKEN_COOKIE_NAME}
      COOKIE_PATH: ${COOKIE_PATH}
      COOKIE_MAX_AGE: ${COOKIE_MAX_AGE}
      COOKIE_SECURE: ${COOKIE_SECURE}
      COOKIE_SAMESITE: ${COOKIE_SAMESITE}
      UPLOAD_DIR: ${UPLOAD_DIR}
      ALLOWED_IMAGE_EXTENSIONS: ${ALLOWED_IMAGE_EXTENSIONS}
      MAX_IMAGE_SIZE: ${MAX_IMAGE_SIZE}
      CORS_ORIGINS: ${CORS_ORIGINS}
    depends_on:
      postgres:
        condition: service_healthy

  frontend:
    build:
      context: ..
      dockerfile: docker/frontend.Dockerfile
    ports:
      - "5173:5173"
    volumes:
      - ../frontend/src:/app/src
      - ../frontend/public:/app/public
    environment:
      VITE_API_BASE_URL: ${VITE_API_BASE_URL}

volumes:
  postgres_data:
```

- [ ] **Step 2: Commit**

```bash
git add docker/docker-compose.yml
git commit -m "feat: add Docker Compose with all services"
```

---

### Task 5: Create Docker README

**Covers:** Documentation

**Files:**
- Create: `docker/README.md`

- [ ] **Step 1: Create docker/README.md**

```markdown
# Docker Development Environment

## Quick Start

```bash
cd docker
cp .env.docker .env
docker compose up --build
```

## Services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | React + Vite dev server |
| Backend | http://localhost:8000 | FastAPI + uvicorn |
| Database | localhost:5432 | PostgreSQL 16 |

## Development

- **Hot-reload**: Both backend and frontend have source directories mounted as volumes. Changes are reflected immediately.
- **Migrations**: Backend automatically runs `alembic upgrade head` on startup.
- **Database Data**: Persisted in `postgres_data` named volume. Survives container restarts.

## Commands

```bash
# Start all services
docker compose up --build

# Start in background
docker compose up -d --build

# Stop all services
docker compose down

# Stop and remove volumes (fresh start)
docker compose down -v

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
```

## Environment Variables

Copy `.env.docker` to `.env` and modify as needed. Key variables:

- `POSTGRES_*`: Database credentials
- `SQLALCHEMY_DATABASE_URL`: Backend database connection
- `SECRET_KEY`: JWT signing key
- `CORS_ORIGINS`: Frontend origin for CORS
- `VITE_API_BASE_URL`: Backend URL for frontend API calls
```

- [ ] **Step 2: Commit**

```bash
git add docker/README.md
git commit -m "docs: add Docker development environment README"
```

---

### Task 6: Verify Docker Setup

**Covers:** Verification

**Files:**
- None (verification only)

- [ ] **Step 1: Build and start all services**

```bash
cd docker
cp .env.docker .env
docker compose up --build
```

Expected: All three containers start successfully.

- [ ] **Step 2: Verify backend is running**

```bash
curl http://localhost:8000/docs
```

Expected: FastAPI Swagger UI loads.

- [ ] **Step 3: Verify frontend is running**

```bash
curl http://localhost:5173
```

Expected: Vite dev server responds with HTML.

- [ ] **Step 4: Verify database connection**

```bash
docker compose exec postgres psql -U antique_user -d antique_marketplace -c "\dt"
```

Expected: Database tables listed (after migrations run).

- [ ] **Step 5: Commit final state**

```bash
git add -A
git commit -m "feat: complete Docker development environment setup"
```
