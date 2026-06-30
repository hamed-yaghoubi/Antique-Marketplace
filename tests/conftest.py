import os
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# Set test environment variables before any app imports
os.environ["SQLALCHEMY_DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ALGORITHM"] = "HS256"
os.environ["UPLOAD_DIR"] = "test_uploads/"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"
os.environ["COOKIE_SECURE"] = "false"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"

from src.db.base import Base
from src.main import app
from src.dependencies.db import get_db
from src.core import security
from src.users.models import User
from src.users.role import UserRole
from src.products.models import Product, ProductImage
from src.products.category import ProductCategory
from src.cart.models import CartItem
from src.orders.models import Order, OrderItem
from src.orders.orderstatus import OrderStatus

# In-memory SQLite engine for tests
test_engine = create_engine("sqlite://", connect_args={"check_same_thread": False})


@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all tables once per test session."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def db_session():
    """Create a fresh database session for each test using nested transactions."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)

    yield session

    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """Create a test client with overridden database dependency."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def user_factory(db_session):
    """Factory fixture to create users."""

    def _create_user(
        username: str = "testuser",
        password: str = "TestPass123!",
        role: UserRole = UserRole.USER,
        is_active: bool = True,
    ) -> User:
        user = User(
            username=username,
            hashed_password=security.hash_password(password),
            role=role,
            is_active=is_active,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user


@pytest.fixture()
def owner_user(user_factory):
    """Create an owner user."""
    return user_factory(username="owner", role=UserRole.OWNER)


@pytest.fixture()
def admin_user(user_factory):
    """Create an admin user."""
    return user_factory(username="admin", role=UserRole.ADMIN)


@pytest.fixture()
def regular_user(user_factory):
    """Create a regular user."""
    return user_factory(username="regular", role=UserRole.USER)


@pytest.fixture()
def other_user(user_factory):
    """Create another regular user for ownership tests."""
    return user_factory(username="other", role=UserRole.USER)


@pytest.fixture()
def product_factory(db_session):
    """Factory fixture to create products."""

    def _create_product(
        title: str = "Test Product",
        description: str = "A test product description",
        price: Decimal = Decimal("99.99"),
        quantity: int = 10,
        category: ProductCategory = ProductCategory.COIN,
        seller_id: int = 1,
        is_active: bool = True,
    ) -> Product:
        product = Product(
            title=title,
            description=description,
            price=price,
            quantity=quantity,
            category=category,
            seller_id=seller_id,
            is_active=is_active,
        )
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        return product

    return _create_product


@pytest.fixture()
def sample_product(product_factory, owner_user):
    """Create a sample product owned by the owner user."""
    return product_factory(seller_id=owner_user.id)


@pytest.fixture()
def cart_item_factory(db_session):
    """Factory fixture to create cart items."""

    def _create_cart_item(
        user_id: int,
        product_id: int,
        quantity: int = 1,
    ) -> CartItem:
        cart_item = CartItem(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
        )
        db_session.add(cart_item)
        db_session.commit()
        db_session.refresh(cart_item)
        return cart_item

    return _create_cart_item


@pytest.fixture()
def order_factory(db_session):
    """Factory fixture to create orders."""

    def _create_order(
        buyer_id: int,
        status: OrderStatus = OrderStatus.PENDING,
        total_price: Decimal = Decimal("0"),
        items: list = None,
    ) -> Order:
        order = Order(
            buyer_id=buyer_id,
            status=status,
            total_price=total_price,
        )
        db_session.add(order)
        db_session.flush()

        if items:
            for item in items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item.get("product_id"),
                    seller_id=item.get("seller_id"),
                    product_title=item.get("product_title", ""),
                    unit_price=item.get("unit_price", Decimal("0")),
                    quantity=item.get("quantity", 1),
                )
                db_session.add(order_item)

        db_session.commit()
        db_session.refresh(order)
        return order

    return _create_order


@pytest.fixture()
def auth_headers(client, regular_user):
    """Get authentication headers for a regular user."""
    response = client.post(
        "/auth/login",
        json={"username": regular_user.username, "password": "TestPass123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def owner_headers(client, owner_user):
    """Get authentication headers for an owner user."""
    response = client.post(
        "/auth/login",
        json={"username": owner_user.username, "password": "TestPass123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin_headers(client, admin_user):
    """Get authentication headers for an admin user."""
    response = client.post(
        "/auth/login",
        json={"username": admin_user.username, "password": "TestPass123!"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
