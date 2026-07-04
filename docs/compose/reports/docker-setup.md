---
feature: docker-setup
status: delivered
specs: []
plans:
  - ../plans/2026-07-04-docker-setup.md
branch: main
commits: pending
---

# Docker Development Environment — Final Report

## What Was Built

A complete Docker development environment for the Antique Marketplace project. The setup includes three services orchestrated via Docker Compose: a PostgreSQL 16 database for persistent data storage, a FastAPI backend with automatic database migrations and hot-reload capabilities, and a React/Vite frontend development server with hot-reload. All services are configured to work together out of the box with a single command.

## Architecture

### Services

| Service | Port | Image | Purpose |
|---------|------|-------|---------|
| postgres | 5432 | postgres:16-alpine | PostgreSQL database |
| backend | 8000 | python:3.14-slim | FastAPI + uvicorn |
| frontend | 5173 | node:20-slim | Vite dev server |

### File Structure

```
docker/
├── .env.docker          # Environment variables for all services
├── backend.Dockerfile   # Backend container build
├── frontend.Dockerfile  # Frontend container build
├── docker-compose.yml   # Service orchestration
├── entrypoint.sh        # Backend startup script
└── README.md            # Usage documentation
```

### Data Flow

- Backend connects to PostgreSQL via `postgres:5432` (Docker network)
- Frontend calls backend API at `http://localhost:8000`
- Source directories are mounted as volumes for hot-reload
- Database data persists in `postgres_data` named volume

### Design Decisions

- **Single compose file**: All services in one `docker-compose.yml` for simplicity in development
- **No Nginx**: Direct access to services on their ports — simpler for local development
- **Auto-migrations**: Backend entrypoint runs `alembic upgrade head` on startup — no manual migration step needed
- **Named volume for PostgreSQL**: Data survives container restarts, can be wiped with `docker compose down -v`

## Usage

### Quick Start

```bash
cd docker
cp .env.docker .env
docker compose up --build
```

### Services

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Backend Docs**: http://localhost:8000/docs
- **Database**: localhost:5432

### Common Commands

```bash
# Start all services
docker compose up --build

# Start in background
docker compose up -d --build

# Stop all services
docker compose down

# Fresh start (remove database data)
docker compose down -v

# View logs
docker compose logs -f
```

### Environment Variables

Copy `.env.docker` to `.env` and modify as needed. Key variables:

- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: Database credentials
- `SQLALCHEMY_DATABASE_URL`: Backend database connection string
- `SECRET_KEY`: JWT signing key (change in production)
- `CORS_ORIGINS`: Frontend origin for CORS (default: `http://localhost:5173`)
- `VITE_API_BASE_URL`: Backend URL for frontend API calls

## Verification

1. **Compose validation**: `docker compose config --quiet` passes (after copying `.env.docker` to `.env`)
2. **Docker availability**: Docker 29.4.2 and Docker Compose v5.1.3 confirmed
3. **All files created**: `.env.docker`, `backend.Dockerfile`, `frontend.Dockerfile`, `docker-compose.yml`, `entrypoint.sh`, `README.md`
4. **Line endings**: `entrypoint.sh` converted to Unix line endings for Linux container compatibility

## Journey Log

- [lesson] Windows line endings in shell scripts cause issues in Linux containers — always convert to Unix format
