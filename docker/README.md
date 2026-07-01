# Docker Setup

Docker configuration for Antique Marketplace. All Docker-related files are centralized here.

## Quick Start

1. Copy environment variables:
   ```bash
   cp .env.docker .env
   ```
2. Edit `.env` and change default passwords
3. Start development environment:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
   ```


## Run Services

### Development (with hot-reload)

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### Production

```bash
docker compose up -d
```

## Services

### Development

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | React dev server (hot-reload) |
| Backend | http://localhost:8000 | FastAPI server (--reload) |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| Database | localhost:5432 | PostgreSQL |

### Production

| Service | URL | Description |
|---------|-----|-------------|
| Frontend + API | http://localhost | Nginx reverse proxy |
| Database | localhost:5432 | PostgreSQL |

## Environment Variables

See `.env.docker` for all available configuration options. Key variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | Database user | `antique_user` |
| `POSTGRES_PASSWORD` | Database password | `antique_secure_password_change_me` |
| `POSTGRES_DB` | Database name | `antique_marketplace` |
| `SECRET_KEY` | JWT signing key | `your-super-secret-key-change-in-production` |
| `CORS_ORIGINS` | Allowed origins | `http://localhost,http://localhost:80` |

**Important:** Always change default passwords before production deployment!

## File Structure

```
docker/
├── backend/Dockerfile         # Backend multi-stage build
├── frontend/Dockerfile        # Frontend multi-stage build
├── nginx/default.conf         # Nginx reverse proxy config
├── docker-compose.yml         # Production configuration
├── docker-compose.dev.yml     # Development overrides
├── .env.docker                # Environment variables template
└── README.md                  # This file
```

## Architecture

- **Backend**: Python 3.14 + FastAPI, multi-stage build (builder → production)
- **Frontend**: React 18 + Vite, multi-stage build (builder → Nginx/Node dev)
- **Database**: PostgreSQL 16 Alpine with persistent volumes
- **Reverse Proxy**: Nginx (production only) — serves frontend, proxies /api/* to backend
- **Auto-migration**: Backend runs `alembic upgrade head` on startup
- **Volumes**: PostgreSQL data and product uploads persist across restarts
