# Backend

FastAPI backend for the Antique Marketplace application.

## Tech Stack

- **Python 3.14**
- **FastAPI** - Modern async web framework
- **SQLAlchemy 2.0** - ORM with mapped columns
- **Alembic** - Database migrations
- **PostgreSQL** - Primary database
- **PyJWT** - JWT authentication
- **pwdlib** - Argon2 password hashing

## Installation

```bash
# Install uv if not already installed
pip install uv

# Install dependencies
uv sync
```

## Environment Variables

Create a `.env` file in the project root:

| Variable | Description | Example |
|----------|-------------|---------|
| `SQLALCHEMY_DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/db` |
| `SECRET_KEY` | JWT secret key | `your-secret-key` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | `7` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:5173` |
| `UPLOAD_DIR` | Image upload directory | `static/uploads` |
| `ALLOWED_IMAGE_EXTENSIONS` | Allowed image types | `.jpg,.jpeg,.png,.webp` |
| `MAX_IMAGE_SIZE` | Max image size in bytes | `5242880` |

## Running

```bash
# Start development server
uvicorn src.main:app --reload

# Run database migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

## Docker

The backend can also be run via Docker. See [docker/README.md](../docker/README.md) for setup instructions.

```bash
cd docker
docker compose -f docker-compose.yml -f docker-compose.dev.yml up backend
```

## API Endpoints

### Auth (`/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register new user |
| POST | `/login` | Login and get tokens |
| POST | `/refresh` | Refresh access token |
| POST | `/logout` | Logout and clear tokens |
| GET | `/me` | Get current user |
| PATCH | `/change-password` | Change password |

### Products (`/products`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List products (with filters) |
| GET | `/{id}` | Get product details |
| POST | `/` | Create product (authenticated) |
| PATCH | `/{id}` | Update product (owner) |
| DELETE | `/{id}` | Delete product (owner) |
| GET | `/me` | Get current user's products |
| POST | `/{id}/images` | Upload product image |
| DELETE | `/{id}/images/{image_id}` | Delete product image |

### Cart (`/cart`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Get user's cart |
| POST | `/items` | Add item to cart |
| PATCH | `/items/{id}` | Update cart item quantity |
| DELETE | `/items/{id}` | Remove item from cart |
| DELETE | `/` | Clear cart |

### Orders (`/orders`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Create order from cart |
| GET | `/` | List user's orders |
| GET | `/{id}` | Get order details |
| PATCH | `/{id}/status` | Update order status |

### Admin (`/admin`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | List all users |
| GET | `/users/{id}` | Get user details |
| PATCH | `/users/{id}/ban` | Ban user |
| PATCH | `/users/{id}/unban` | Unban user |
| DELETE | `/products/{id}` | Delete product (admin only, cannot delete admin/owner products) |
| POST | `/promote/{user_id}` | Promote user to admin (owner only) |

### Owner (`/owner`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/promote/{user_id}` | Promote user to admin |

## Project Structure

```
src/
├── main.py              # FastAPI app entry point
├── auth/                # Authentication module
│   ├── router.py
│   ├── service.py
│   └── schemas.py
├── users/               # User management
│   ├── models.py
│   ├── service.py
│   ├── repository.py
│   ├── schemas.py
│   └── role.py
├── products/            # Product CRUD
│   ├── models.py
│   ├── router.py
│   ├── service.py
│   ├── repository.py
│   ├── schemas.py
│   └── category.py
├── cart/                # Shopping cart
│   ├── models.py
│   ├── router.py
│   ├── service.py
│   ├── repository.py
│   └── schemas.py
├── orders/              # Order management
│   ├── models.py
│   ├── router.py
│   ├── service.py
│   ├── repository.py
│   ├── schemas.py
│   └── orderstatus.py
├── admin/               # Admin panel
│   ├── router.py
│   ├── service.py
│   └── repository.py
├── owner/               # Owner dashboard (promote only)
│   └── router.py
├── core/                # Configuration
│   ├── config.py
│   ├── security.py
│   └── exceptions.py
├── db/                  # Database setup
│   ├── base.py
│   └── session.py
└── dependencies/        # FastAPI dependencies
    ├── auth.py
    └── db.py
```

## Architecture

Each domain module follows a layered pattern:
- **router.py** - API endpoint definitions
- **service.py** - Business logic
- **repository.py** - Database queries
- **schemas.py** - Pydantic models for request/response
- **models.py** - SQLAlchemy database models
