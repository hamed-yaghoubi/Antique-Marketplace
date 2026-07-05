# Docker Setup Guide

## Quick Start

```bash
# 1. Clone and setup
git clone <repo-url>
cd Antique-Marketplace

# 2. Setup environment
cp .env.example .env
# Edit .env - change database URL for Docker:
# SQLALCHEMY_DATABASE_URL = postgresql+psycopg://user:pass@db:5432/db

# 3. Start all services
docker compose up --build
```

**Services:**

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:3000 | 3000 |
| Backend API | http://localhost:8000/docs | 8000 |
| PostgreSQL | localhost:5432 | 5432 |

## First Run

On first `docker compose up --build`:
1. PostgreSQL initializes with user `user`, password `pass`, database `db`
2. Backend runs `alembic upgrade head` (applies all migrations)
3. Frontend starts Vite dev server

## Hot Reload

Both services support hot reload:
- **Backend**: Edit `src/` files → uvicorn auto-restarts
- **Frontend**: Edit `frontend/src/` files → Vite HMR updates browser

## Common Issues & Fixes

### 1. Build fails: "no such host" / DNS errors

Docker can't reach Docker Hub or PyPI.

**Fix:** Check your internet connection, then:
```bash
# Pull images manually first
docker pull python:latest
docker pull node:alpine
docker pull postgres:16-alpine

# Then build
docker compose up --build
```

### 2. Build fails: pip/uv timeout downloading packages

Docker's network proxy is blocking or slowing connections.

**Fix option A** - Build with host network:
```bash
docker build --network=host -f docker/backend.Dockerfile -t antique-backend .
docker build --network=host -f docker/frontend.Dockerfile -t antique-frontend .
docker compose up
```

**Fix option B** - Disable Docker proxy:
1. Open Docker Desktop → Settings → Resources → Proxies
2. Uncheck "Manual proxy configuration"
3. Apply & Restart

**Fix option C** - Use a mirror (Iran/China):
Add to Dockerfile before `pip install`:
```dockerfile
ENV PIP_INDEX_URL=https://mirrors.cloud.aliyuncs.com/pypi/simple/
```

### 3. Backend can't connect to database

```
SQLALCHEMY_DATABASE_URL = postgresql+psycopg://user:pass@db:5432/db
```

- Host must be `db` (the docker-compose service name), not `localhost`
- Driver must be `+psycopg` (not just `postgresql://`)
- Check `.env` file has this exact format

### 4. Port already in use

```
Error: bind: address already in use
```

**Fix:**
```bash
# Find what's using the port (Windows)
netstat -ano | findstr :8000

# Kill the process or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

### 5. Changes not reflecting

**Backend:** If uvicorn doesn't restart:
```bash
docker compose restart backend
```

**Frontend:** If HMR stops working:
```bash
docker compose restart frontend
```

### 6. Permission denied on static/

```bash
# Fix static directory permissions
docker compose exec backend chmod -R 755 /app/static
```

### 7. Database migrations not running

```bash
# Run migrations manually
docker compose exec backend uv run alembic upgrade head

# Create new migration
docker compose exec backend uv run alembic revision --autogenerate -m "description"
```

### 8. Docker build cache is stale

```bash
# Full clean rebuild
docker compose down
docker compose build --no-cache
docker compose up
```

### 9. "COPY failed: file not found" errors

File doesn't exist or is excluded by `.dockerignore`. Check:
```bash
# See what's in build context
docker build --no-cache -f docker/backend.Dockerfile . 2>&1 | head -20
```

### 10. uv/pip install fails inside Docker

Network issues inside container. Try:
```bash
# Build with host networking
docker build --network=host -f docker/backend.Dockerfile .
```

## Useful Commands

```bash
# Start in background
docker compose up -d

# View logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db

# Stop all
docker compose down

# Stop and remove volumes (fresh DB)
docker compose down -v

# Rebuild single service
docker compose build backend
docker compose up backend

# Shell into container
docker compose exec backend sh
docker compose exec frontend sh
docker compose exec db psql -U user -d db

# Check container status
docker compose ps
```

## Environment Variables

Key variables for Docker (in `.env`):

```bash
# Database - use 'db' as host, not localhost
SQLALCHEMY_DATABASE_URL = postgresql+psycopg://user:pass@db:5432/db

# Backend
SECRET_KEY = your-secret-key
CORS_ORIGINS = http://localhost:3000

# Frontend (in frontend/.env)
VITE_API_BASE_URL = http://localhost:8000
```
