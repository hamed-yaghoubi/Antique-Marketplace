# Tests

Automated test suite for the Antique Marketplace backend.

## Setup

Install dev dependencies:

```bash
uv sync --group dev
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run a specific module
uv run pytest tests/test_schemas.py -v
uv run pytest tests/test_repositories.py -v
uv run pytest tests/test_services.py -v
uv run pytest tests/test_routes_auth.py -v

# Run a specific test class
uv run pytest tests/test_services.py::TestOrderService -v

# Run a specific test
uv run pytest tests/test_services.py::TestOrderService::test_create_order -v

# Stop on first failure
uv run pytest -x

# Show only failures
uv run pytest --tb=short
```

## Test Files

| File | Module | Tests | Description |
|------|--------|-------|-------------|
| `test_schemas.py` | Schemas | 42 | Pydantic validation, serialization, required fields, invalid input |
| `test_repositories.py` | Repository | 50 | CRUD operations, database constraints, filtering, pagination |
| `test_services.py` | Service | 64 | Business rules, auth flow, ownership, stock validation, exceptions |
| `test_routes_auth.py` | API Routes | 19 | Auth endpoints: register, login, refresh, me, change-password |
| `test_routes_products.py` | API Routes | 20 | Product CRUD, list/filter, ownership, authentication |
| `test_routes_cart.py` | API Routes | 13 | Cart read, add, update, remove, clear |
| `test_routes_orders.py` | API Routes | 14 | Order create, list, detail, cancel |
| `test_routes_admin.py` | API Routes | 12 | Admin user management, ban/unban, hierarchy |
| **Total** | | **234** | |

## Infrastructure

- **Database**: In-memory SQLite (no external DB required)
- **Isolation**: Each test runs in a rolled-back transaction
- **Fixtures**: Factories for users, products, cart items, orders; auth header helpers
- **No mocking**: Real business logic tested against a real database

## Fixtures

Defined in `conftest.py`:

| Fixture | Scope | Description |
|---------|-------|-------------|
| `db_session` | function | Fresh SQLAlchemy session, rolled back after each test |
| `client` | function | FastAPI TestClient with overridden DB dependency |
| `user_factory` | function | Creates users with configurable role/status |
| `owner_user` | function | Pre-created owner role user |
| `admin_user` | function | Pre-created admin role user |
| `regular_user` | function | Pre-created regular user |
| `other_user` | function | Second regular user for ownership tests |
| `product_factory` | function | Creates products with configurable fields |
| `sample_product` | function | Product owned by owner_user |
| `cart_item_factory` | function | Creates cart items |
| `order_factory` | function | Creates orders with optional items |
| `auth_headers` | function | Bearer token headers for regular_user |
| `owner_headers` | function | Bearer token headers for owner_user |
| `admin_headers` | function | Bearer token headers for admin_user |
