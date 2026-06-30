"""Schema validation tests for all domains."""
from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.users.schemas import UserCreate, UserResponse, UserUpdate
from src.users.role import UserRole
from src.auth.schemas import (
    LoginRequest,
    TokenPayload,
    TokenResponse,
    ChangePasswordRequest,
)
from src.products.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductCard,
    ProductImageResponse,
    ProductFilter,
    PaginationParams,
)
from src.products.category import ProductCategory
from src.cart.schemas import CartItemCreate, CartItemUpdate, CartResponse, CartItemResponse
from src.orders.schemas import OrderResponse, OrderItemResponse, OrderStatusUpdate, OrderCard
from src.orders.orderstatus import OrderStatus


# ──────────────────────────────────────────────────────────────
# User Schemas
# ──────────────────────────────────────────────────────────────


class TestUserCreate:
    def test_valid_user_create(self):
        user = UserCreate(username="alice", password="Secret123!", confirm_password="Secret123!")
        assert user.username == "alice"
        assert user.password == "Secret123!"

    def test_passwords_must_match(self):
        with pytest.raises(ValidationError, match="Passwords do not match"):
            UserCreate(username="alice", password="Secret123!", confirm_password="Different123!")

    def test_missing_username(self):
        with pytest.raises(ValidationError):
            UserCreate(password="Secret123!", confirm_password="Secret123!")

    def test_missing_password(self):
        with pytest.raises(ValidationError):
            UserCreate(username="alice", confirm_password="Secret123!")

    def test_missing_confirm_password(self):
        with pytest.raises(ValidationError):
            UserCreate(username="alice", password="Secret123!")


class TestUserResponse:
    def test_from_attributes(self):
        data = {
            "id": 1,
            "username": "alice",
            "role": "user",
            "is_active": True,
            "created_at": datetime.now(),
        }
        response = UserResponse.model_validate(data)
        assert response.id == 1
        assert response.username == "alice"
        assert response.role == UserRole.USER

    def test_invalid_role(self):
        data = {
            "id": 1,
            "username": "alice",
            "role": "superadmin",
            "is_active": True,
            "created_at": datetime.now(),
        }
        with pytest.raises(ValidationError):
            UserResponse.model_validate(data)


class TestUserUpdate:
    def test_valid_update(self):
        update = UserUpdate(username="newname")
        assert update.username == "newname"

    def test_all_none_by_default(self):
        update = UserUpdate()
        assert update.username is None

    def test_partial_update(self):
        update = UserUpdate(username="newname")
        dumped = update.model_dump(exclude_unset=True)
        assert "username" in dumped


# ──────────────────────────────────────────────────────────────
# Auth Schemas
# ──────────────────────────────────────────────────────────────


class TestLoginRequest:
    def test_valid_login(self):
        data = LoginRequest(username="alice", password="secret")
        assert data.username == "alice"

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            LoginRequest(username="alice")


class TestTokenResponse:
    def test_defaults(self):
        token = TokenResponse(access_token="abc", refresh_token="xyz")
        assert token.token_type == "bearer"


class TestTokenPayload:
    def test_valid_payload(self):
        payload = TokenPayload(sub="1", exp=datetime.now(), type="access")
        assert payload.sub == "1"


class TestChangePasswordRequest:
    def test_valid_change(self):
        data = ChangePasswordRequest(
            current_password="old",
            new_password="new",
            confirm_password="new",
        )
        assert data.current_password == "old"

    def test_passwords_must_match(self):
        with pytest.raises(ValidationError, match="Passwords do not match"):
            ChangePasswordRequest(
                current_password="old",
                new_password="new",
                confirm_password="different",
            )

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            ChangePasswordRequest(current_password="old")


# ──────────────────────────────────────────────────────────────
# Product Schemas
# ──────────────────────────────────────────────────────────────


class TestProductCreate:
    def test_valid_product(self):
        product = ProductCreate(
            title="Antique Clock",
            description="Beautiful grandfather clock",
            price=Decimal("250.00"),
            quantity=5,
            category=ProductCategory.CLOCK,
        )
        assert product.title == "Antique Clock"
        assert product.price == Decimal("250.00")

    def test_missing_title(self):
        with pytest.raises(ValidationError):
            ProductCreate(
                description="desc",
                price=Decimal("10.00"),
                quantity=1,
                category=ProductCategory.CLOCK,
            )

    def test_invalid_category(self):
        with pytest.raises(ValidationError):
            ProductCreate(
                title="Item",
                description="desc",
                price=Decimal("10.00"),
                quantity=1,
                category="invalid_category",
            )

    def test_negative_quantity_not_rejected_at_schema_level(self):
        """Note: The schema does not enforce ge=0 on quantity. Negative values
        pass schema validation but should be caught at the service/DB level."""
        product = ProductCreate(
            title="Item",
            description="desc",
            price=Decimal("10.00"),
            quantity=-1,
            category=ProductCategory.BOOK,
        )
        assert product.quantity == -1

    def test_zero_quantity_allowed(self):
        product = ProductCreate(
            title="Item",
            description="desc",
            price=Decimal("10.00"),
            quantity=0,
            category=ProductCategory.BOOK,
        )
        assert product.quantity == 0


class TestProductUpdate:
    def test_partial_update(self):
        update = ProductUpdate(title="New Title")
        dumped = update.model_dump(exclude_unset=True)
        assert "title" in dumped
        assert "price" not in dumped

    def test_all_optional(self):
        update = ProductUpdate()
        assert update.title is None
        assert update.price is None
        assert update.quantity is None


class TestProductFilter:
    def test_defaults(self):
        f = ProductFilter()
        assert f.search is None
        assert f.sort_by == "created_at"
        assert f.sort_order == "desc"

    def test_with_filters(self):
        f = ProductFilter(
            category=ProductCategory.COIN,
            min_price=Decimal("10"),
            max_price=Decimal("100"),
        )
        assert f.category == ProductCategory.COIN


class TestPaginationParams:
    def test_defaults(self):
        p = PaginationParams()
        assert p.page == 1
        assert p.page_size == 20

    def test_custom(self):
        p = PaginationParams(page=3, page_size=50)
        assert p.page == 3

    def test_invalid_page(self):
        with pytest.raises(ValidationError):
            PaginationParams(page=0)

    def test_invalid_page_size(self):
        with pytest.raises(ValidationError):
            PaginationParams(page_size=0)

    def test_page_size_too_large(self):
        with pytest.raises(ValidationError):
            PaginationParams(page_size=200)


class TestProductCard:
    def test_from_dict_with_images(self):
        data = {
            "id": 1,
            "title": "Clock",
            "price": Decimal("100"),
            "category": "clock",
            "is_active": True,
            "quantity": 5,
            "seller_id": 1,
            "seller": "alice",
            "images": [{"id": 1, "image_url": "/img.jpg"}],
        }
        card = ProductCard.model_validate(data)
        assert card.main_image is not None
        assert card.main_image.image_url == "/img.jpg"
        assert card.seller == "alice"

    def test_from_dict_no_images(self):
        data = {
            "id": 1,
            "title": "Clock",
            "price": Decimal("100"),
            "category": "clock",
            "is_active": True,
            "quantity": 5,
            "seller_id": 1,
            "seller": "alice",
            "images": [],
        }
        card = ProductCard.model_validate(data)
        assert card.main_image is None


# ──────────────────────────────────────────────────────────────
# Cart Schemas
# ──────────────────────────────────────────────────────────────


class TestCartItemCreate:
    def test_valid(self):
        item = CartItemCreate(product_id=1, quantity=2)
        assert item.quantity == 2

    def test_invalid_quantity(self):
        with pytest.raises(ValidationError):
            CartItemCreate(product_id=1, quantity=0)

    def test_negative_quantity(self):
        with pytest.raises(ValidationError):
            CartItemCreate(product_id=1, quantity=-1)


class TestCartItemUpdate:
    def test_valid(self):
        item = CartItemUpdate(quantity=3)
        assert item.quantity == 3

    def test_invalid_quantity(self):
        with pytest.raises(ValidationError):
            CartItemUpdate(quantity=0)


# ──────────────────────────────────────────────────────────────
# Order Schemas
# ──────────────────────────────────────────────────────────────


class TestOrderStatusUpdate:
    def test_valid_status(self):
        update = OrderStatusUpdate(status=OrderStatus.CANCELLED)
        assert update.status == OrderStatus.CANCELLED

    def test_invalid_status(self):
        with pytest.raises(ValidationError):
            OrderStatusUpdate(status="invalid")


class TestOrderResponse:
    def test_from_attributes(self):
        data = {
            "id": 1,
            "status": "pending",
            "total_price": Decimal("99.99"),
            "created_at": datetime.now(),
            "items": [],
        }
        response = OrderResponse.model_validate(data)
        assert response.status == OrderStatus.PENDING
        assert response.items == []


class TestOrderCard:
    def test_from_attributes(self):
        data = {
            "id": 1,
            "status": "paid",
            "total_price": Decimal("50.00"),
            "created_at": datetime.now(),
        }
        card = OrderCard.model_validate(data)
        assert card.status == OrderStatus.PAID
