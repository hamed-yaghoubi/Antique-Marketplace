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
