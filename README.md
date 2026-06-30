# Antique Marketplace

A full-stack web application for buying and selling antiques with multi-seller support, role-based access control, and a vintage-themed Persian UI.

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python 3.14, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL |
| **Frontend** | React 18, TypeScript, Vite 6, Tailwind CSS, React Router 6 |
| **Testing** | pytest, httpx, SQLite (in-memory) |

## Features

- Multi-seller marketplace with product listings
- JWT authentication with role-based access (User, Admin, Owner)
- Product management with image uploads
- Shopping cart and checkout flow
- Order tracking and status management
- Admin panel for user and product moderation
- Owner dashboard with full system control
- RTL Persian UI with Vazirmatn font
- Filtering, sorting, and pagination

## Prerequisites

- Python 3.14+
- Node.js 18+
- PostgreSQL

## Quick Start

### Backend

```bash
# Install uv package manager
pip install uv

# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the server
uvicorn src.main:app --reload
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your API URL

# Start development server
npm run dev
```

## Project Structure

```
Antique-Marketplace/
├── src/                    # Backend (FastAPI)
│   ├── auth/              # Authentication module
│   ├── users/             # User management
│   ├── products/          # Product CRUD
│   ├── cart/              # Shopping cart
│   ├── orders/            # Order management
│   ├── admin/             # Admin panel
│   ├── owner/             # Owner dashboard
│   ├── core/              # Config, security
│   ├── db/                # Database engine/session
│   └── dependencies/      # FastAPI dependencies
├── tests/                 # Test suite (pytest)
│   ├── conftest.py        # Shared fixtures and test infrastructure
│   ├── test_schemas.py    # Schema validation tests
│   ├── test_repositories.py  # Repository CRUD tests
│   ├── test_services.py   # Service business logic tests
│   ├── test_routes_auth.py   # Auth API endpoint tests
│   ├── test_routes_products.py  # Product API endpoint tests
│   ├── test_routes_cart.py  # Cart API endpoint tests
│   ├── test_routes_orders.py  # Order API endpoint tests
│   └── test_routes_admin.py  # Admin API endpoint tests
├── frontend/              # Frontend (React)
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Route pages
│   │   ├── utils/         # Utility functions
│   │   ├── types/         # TypeScript types
│   │   └── api/           # API client
│   └── ...
├── migrations/            # Alembic migrations
└── static/                # Uploaded files
```

## Testing

Install dev dependencies and run the test suite:

```bash
# Install dev dependencies
uv sync --group dev

# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run a specific module
uv run pytest tests/test_services.py -v
```

Tests use an in-memory SQLite database and run in isolated transactions — no external database required.

## Documentation

- [Backend Documentation](src/README.md)
- [Frontend Documentation](frontend/README.md)
- [TestDocumentation](tests/README.md)
