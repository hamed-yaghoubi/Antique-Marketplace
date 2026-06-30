# Antique Marketplace

A full-stack web application for buying and selling antiques with multi-seller support, role-based access control, and a vintage-themed Persian UI.

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Python 3.14, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL |
| **Frontend** | React 18, TypeScript, Vite 6, Tailwind CSS, React Router 6 |

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

## Documentation

- [Backend Documentation](src/README.md)
- [Frontend Documentation](frontend/README.md)
