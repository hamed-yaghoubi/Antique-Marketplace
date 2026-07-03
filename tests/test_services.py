"""Service layer tests — business rules, exceptions, real logic."""
from decimal import Decimal
from unittest.mock import patch, MagicMock

import pytest
from fastapi import HTTPException

from src.core import security
from src.core.exceptions import (
    AppException,
    CartItemNotFoundError,
    EmptyCartError,
    ForbiddenError,
    InsufficientStockError,
    InvalidCredentialsError,
    OrderCannotBeCancelledError,
    OrderNotFoundError,
    ProductNotFoundError,
    SelfDemoteError,
    SelfPurchaseError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.users.models import User
from src.users.role import UserRole
from src.users import service
from src.users.schemas import UserUpdate
from src.products.models import Product
from src.products.category import ProductCategory
from src.products import service as products_service
from src.products.schemas import ProductCreate, ProductUpdate
from src.cart import service as cart_service
from src.cart.schemas import CartItemCreate, CartItemUpdate
from src.orders import service as orders_service
from src.orders.orderstatus import OrderStatus
from src.orders.schemas import OrderStatusUpdate
from src.auth import service as auth_service
from src.auth.schemas import ChangePasswordRequest, LoginRequest



# ──────────────────────────────────────────────────────────────
# User Service
# ──────────────────────────────────────────────────────────────


class TestUserService:
    def test_get_user(self, user_factory, db_session):
        user = user_factory(username="getme")
        found = service.get_user(db_session, user.id)
        assert found.username == "getme"

    def test_get_user_not_found(self, db_session):
        with pytest.raises(UserNotFoundError):
            service.get_user(db_session, 99999)

    def test_get_user_by_username(self, user_factory, db_session):
        user = user_factory(username="byuser")
        found = service.get_user_by_username(db_session, "byuser")
        assert found.id == user.id

    def test_get_user_by_username_not_found(self, db_session):
        with pytest.raises(UserNotFoundError):
            service.get_user_by_username(db_session, "nobody")

    def test_update_user(self, user_factory, db_session):
        user = user_factory(username="oldname")
        update = UserUpdate(username="newname")
        updated = service.update_user(db_session, user, update)
        assert updated.username == "newname"

    def test_update_user_no_changes(self, user_factory, db_session):
        user = user_factory(username="nochange")
        update = UserUpdate()
        updated = service.update_user(db_session, user, update)
        assert updated.username == "nochange"

    def test_delete_user(self, user_factory, db_session):
        user = user_factory(username="deleteme")
        service.delete_user(db_session, user)
        with pytest.raises(UserNotFoundError):
            service.get_user(db_session, user.id)


# ──────────────────────────────────────────────────────────────
# Auth Service
# ──────────────────────────────────────────────────────────────


class TestAuthService:
    def test_register_first_user_gets_owner(self, db_session):
        from src.users.schemas import UserCreate
        data = UserCreate(username="first", password="Pass123!", confirm_password="Pass123!")
        user = auth_service.register(db_session, data)
        assert user.role == UserRole.OWNER

    def test_register_subsequent_user_gets_user_role(self, user_factory, db_session):
        user_factory(username="existing")
        from src.users.schemas import UserCreate
        data = UserCreate(username="second", password="Pass123!", confirm_password="Pass123!")
        user = auth_service.register(db_session, data)
        assert user.role == UserRole.USER

    def test_register_duplicate_username(self, user_factory, db_session):
        user_factory(username="dupe")
        from src.users.schemas import UserCreate
        data = UserCreate(username="dupe", password="Pass123!", confirm_password="Pass123!")
        with pytest.raises(UserAlreadyExistsError):
            auth_service.register(db_session, data)

    def test_login_success(self, user_factory, db_session):
        user_factory(username="logintest")
        data = LoginRequest(username="logintest", password="TestPass123!")
        tokens = auth_service.login(db_session, data)
        assert tokens.access_token
        assert tokens.refresh_token
        assert tokens.token_type == "bearer"

    def test_login_wrong_password(self, user_factory, db_session):
        user_factory(username="wrongpass")
        data = LoginRequest(username="wrongpass", password="WrongPassword!")
        with pytest.raises(InvalidCredentialsError):
            auth_service.login(db_session, data)

    def test_login_nonexistent_user(self, db_session):
        data = LoginRequest(username="ghost", password="Pass!")
        with pytest.raises(InvalidCredentialsError):
            auth_service.login(db_session, data)

    def test_login_banned_user(self, user_factory, db_session):
        user_factory(username="banned", is_active=False)
        data = LoginRequest(username="banned", password="TestPass123!")
        with pytest.raises(AppException) as exc_info:
            auth_service.login(db_session, data)
        assert exc_info.value.status_code == 403

    def test_refresh_tokens_valid(self, user_factory, db_session):
        user_factory(username="refresh")
        data = LoginRequest(username="refresh", password="TestPass123!")
        tokens = auth_service.login(db_session, data)
        new_tokens = auth_service.refresh_tokens(db_session, tokens.refresh_token)
        assert new_tokens.access_token
        assert new_tokens.refresh_token
        assert new_tokens.token_type == "bearer"
        # Verify the new access token can be decoded successfully
        payload = security.decode_access_token(new_tokens.access_token)
        assert "sub" in payload

    def test_refresh_tokens_invalid(self, db_session):
        with pytest.raises(AppException) as exc_info:
            auth_service.refresh_tokens(db_session, "invalid.token.here")
        assert exc_info.value.status_code == 401

    def test_refresh_tokens_nonexistent_user(self, user_factory, db_session):
        user_factory(username="temp")
        data = LoginRequest(username="temp", password="TestPass123!")
        tokens = auth_service.login(db_session, data)
        # Delete user then try refresh
        from src.users import repository
        user = repository.get_by_username(db_session, "temp")
        repository.delete(db_session, user)
        with pytest.raises(AppException) as exc_info:
            auth_service.refresh_tokens(db_session, tokens.refresh_token)
        assert exc_info.value.status_code == 401

    def test_change_password_success(self, user_factory, db_session):
        user = user_factory(username="changepass")
        data = ChangePasswordRequest(
            current_password="TestPass123!",
            new_password="NewPass456!",
            confirm_password="NewPass456!",
        )
        auth_service.change_password(db_session, user, data)
        # Verify old password no longer works
        assert not security.verify_password("TestPass123!", user.hashed_password)
        assert security.verify_password("NewPass456!", user.hashed_password)

    def test_change_password_wrong_current(self, user_factory, db_session):
        user = user_factory(username="wrongold")
        data = ChangePasswordRequest(
            current_password="WrongOld!",
            new_password="NewPass1!",
            confirm_password="NewPass1!",
        )
        with pytest.raises(InvalidCredentialsError):
            auth_service.change_password(db_session, user, data)


# ──────────────────────────────────────────────────────────────
# Product Service
# ──────────────────────────────────────────────────────────────


class TestProductService:
    def test_get_product(self, product_factory, owner_user, db_session):
        product = product_factory(title="Find", seller_id=owner_user.id)
        found = products_service.get_product(db_session, product.id)
        assert found.title == "Find"

    def test_get_product_not_found(self, db_session):
        with pytest.raises(ProductNotFoundError):
            products_service.get_product(db_session, 99999)

    def test_create_product(self, owner_user, db_session):
        data = ProductCreate(
            title="New",
            description="Desc",
            price=Decimal("50.00"),
            quantity=5,
            category=ProductCategory.COIN,
        )
        product = products_service.create_product(db_session, data, owner_user)
        assert product.title == "New"
        assert product.seller_id == owner_user.id

    def test_update_product_owner(self, product_factory, owner_user, db_session):
        product = product_factory(title="Old", seller_id=owner_user.id)
        data = ProductUpdate(title="New")
        updated = products_service.update_product(db_session, product.id, data, owner_user)
        assert updated.title == "New"

    def test_update_product_not_owner(self, product_factory, owner_user, other_user, db_session):
        product = product_factory(title="NotYours", seller_id=owner_user.id)
        data = ProductUpdate(title="Hacked")
        with pytest.raises(ForbiddenError):
            products_service.update_product(db_session, product.id, data, other_user)

    def test_update_product_not_found(self, owner_user, db_session):
        data = ProductUpdate(title="Ghost")
        with pytest.raises(ProductNotFoundError):
            products_service.update_product(db_session, 99999, data, owner_user)

    def test_delete_product_owner(self, product_factory, owner_user, db_session):
        product = product_factory(title="Delete", seller_id=owner_user.id)
        products_service.delete_product(db_session, product.id, owner_user)
        with pytest.raises(ProductNotFoundError):
            products_service.get_product(db_session, product.id)

    def test_delete_product_not_owner(self, product_factory, owner_user, other_user, db_session):
        product = product_factory(title="NotYours", seller_id=owner_user.id)
        with pytest.raises(ForbiddenError):
            products_service.delete_product(db_session, product.id, other_user)

    def test_delete_product_not_found(self, owner_user, db_session):
        with pytest.raises(ProductNotFoundError):
            products_service.delete_product(db_session, 99999, owner_user)


# ──────────────────────────────────────────────────────────────
# Cart Service
# ──────────────────────────────────────────────────────────────


class TestCartService:
    def test_get_cart_empty(self, regular_user, db_session):
        result = cart_service.get_cart(db_session, regular_user)
        assert result.items == []
        assert result.total_price == Decimal("0")

    def test_add_item(self, regular_user, sample_product, db_session):
        data = CartItemCreate(product_id=sample_product.id, quantity=2)
        item = cart_service.add_item(db_session, data, regular_user)
        assert item.quantity == 2

    def test_add_item_merges_quantity(self, regular_user, sample_product, db_session):
        data = CartItemCreate(product_id=sample_product.id, quantity=2)
        cart_service.add_item(db_session, data, regular_user)
        data2 = CartItemCreate(product_id=sample_product.id, quantity=3)
        item = cart_service.add_item(db_session, data2, regular_user)
        assert item.quantity == 5

    def test_add_item_insufficient_stock(self, regular_user, sample_product, db_session):
        data = CartItemCreate(product_id=sample_product.id, quantity=999)
        with pytest.raises(InsufficientStockError):
            cart_service.add_item(db_session, data, regular_user)

    def test_add_item_merged_exceeds_stock(self, regular_user, sample_product, db_session):
        data = CartItemCreate(product_id=sample_product.id, quantity=8)
        cart_service.add_item(db_session, data, regular_user)
        data2 = CartItemCreate(product_id=sample_product.id, quantity=5)
        with pytest.raises(InsufficientStockError):
            cart_service.add_item(db_session, data2, regular_user)

    def test_add_item_product_not_found(self, regular_user, db_session):
        data = CartItemCreate(product_id=99999, quantity=1)
        with pytest.raises(ProductNotFoundError):
            cart_service.add_item(db_session, data, regular_user)

    def test_add_item_self_purchase(self, owner_user, product_factory, db_session):
        product = product_factory(title="Own", seller_id=owner_user.id)
        data = CartItemCreate(product_id=product.id, quantity=1)
        with pytest.raises(SelfPurchaseError):
            cart_service.add_item(db_session, data, owner_user)

    def test_update_item_quantity(self, cart_item_factory, regular_user, sample_product, db_session):
        item = cart_item_factory(user_id=regular_user.id, product_id=sample_product.id, quantity=1)
        data = CartItemUpdate(quantity=5)
        updated = cart_service.update_item_quantity(db_session, item.id, data, regular_user)
        assert updated.quantity == 5

    def test_update_item_not_found(self, regular_user, db_session):
        data = CartItemUpdate(quantity=1)
        with pytest.raises(CartItemNotFoundError):
            cart_service.update_item_quantity(db_session, 99999, data, regular_user)

    def test_update_item_not_owner(self, cart_item_factory, regular_user, other_user, sample_product, db_session):
        item = cart_item_factory(user_id=regular_user.id, product_id=sample_product.id)
        data = CartItemUpdate(quantity=1)
        with pytest.raises(ForbiddenError):
            cart_service.update_item_quantity(db_session, item.id, data, other_user)

    def test_update_item_insufficient_stock(self, cart_item_factory, regular_user, sample_product, db_session):
        item = cart_item_factory(user_id=regular_user.id, product_id=sample_product.id)
        data = CartItemUpdate(quantity=999)
        with pytest.raises(InsufficientStockError):
            cart_service.update_item_quantity(db_session, item.id, data, regular_user)

    def test_remove_item(self, cart_item_factory, regular_user, sample_product, db_session):
        item = cart_item_factory(user_id=regular_user.id, product_id=sample_product.id)
        cart_service.remove_item(db_session, item.id, regular_user)
        from src.cart import repository
        assert repository.get_by_id(db_session, item.id) is None

    def test_remove_item_not_found(self, regular_user, db_session):
        with pytest.raises(CartItemNotFoundError):
            cart_service.remove_item(db_session, 99999, regular_user)

    def test_remove_item_not_owner(self, cart_item_factory, regular_user, other_user, sample_product, db_session):
        item = cart_item_factory(user_id=regular_user.id, product_id=sample_product.id)
        with pytest.raises(ForbiddenError):
            cart_service.remove_item(db_session, item.id, other_user)

    def test_clear_cart(self, cart_item_factory, regular_user, sample_product, db_session):
        cart_item_factory(user_id=regular_user.id, product_id=sample_product.id)
        cart_service.clear_cart(db_session, regular_user)
        result = cart_service.get_cart(db_session, regular_user)
        assert result.items == []

    def test_get_cart_with_items(self, cart_item_factory, regular_user, sample_product, db_session):
        cart_item_factory(user_id=regular_user.id, product_id=sample_product.id, quantity=2)
        result = cart_service.get_cart(db_session, regular_user)
        assert len(result.items) == 1
        expected_total = sample_product.price * 2
        assert result.total_price == expected_total


# ──────────────────────────────────────────────────────────────
# Order Service
# ──────────────────────────────────────────────────────────────


class TestOrderService:
    def test_create_order(self, cart_item_factory, regular_user, sample_product, db_session):
        original_quantity = sample_product.quantity
        cart_item_factory(user_id=regular_user.id, product_id=sample_product.id, quantity=2)
        order = orders_service.create_order(db_session, regular_user)
        assert order.status == OrderStatus.PENDING
        assert order.total_price == sample_product.price * 2
        assert len(order.items) == 1
        # Verify stock was decremented
        db_session.refresh(sample_product)
        assert sample_product.quantity == original_quantity - 2

    def test_create_order_empty_cart(self, regular_user, db_session):
        with pytest.raises(EmptyCartError):
            orders_service.create_order(db_session, regular_user)

    def test_create_order_insufficient_stock(self, cart_item_factory, regular_user, sample_product, db_session):
        cart_item_factory(user_id=regular_user.id, product_id=sample_product.id, quantity=999)
        with pytest.raises(InsufficientStockError):
            orders_service.create_order(db_session, regular_user)

    def test_create_order_clears_cart(self, cart_item_factory, regular_user, sample_product, db_session):
        cart_item_factory(user_id=regular_user.id, product_id=sample_product.id, quantity=1)
        orders_service.create_order(db_session, regular_user)
        from src.cart import repository
        items = repository.get_by_user_id(db_session, regular_user.id)
        assert items == []

    def test_create_order_self_purchase(self, owner_user, product_factory, cart_item_factory, db_session):
        product = product_factory(title="Own", seller_id=owner_user.id, quantity=5)
        cart_item_factory(user_id=owner_user.id, product_id=product.id, quantity=1)
        with pytest.raises(SelfPurchaseError):
            orders_service.create_order(db_session, owner_user)

    def test_get_orders(self, order_factory, regular_user, db_session):
        order_factory(buyer_id=regular_user.id, total_price=Decimal("50"))
        order_factory(buyer_id=regular_user.id, total_price=Decimal("100"))
        orders = orders_service.get_orders(db_session, regular_user)
        assert len(orders) >= 2

    def test_get_order(self, order_factory, regular_user, db_session):
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"))
        found = orders_service.get_order(db_session, order.id, regular_user)
        assert found.id == order.id

    def test_get_order_not_found(self, regular_user, db_session):
        with pytest.raises(OrderNotFoundError):
            orders_service.get_order(db_session, 99999, regular_user)

    def test_get_order_not_owner(self, order_factory, regular_user, other_user, db_session):
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"))
        with pytest.raises(ForbiddenError):
            orders_service.get_order(db_session, order.id, other_user)

    def test_cancel_order(self, order_factory, product_factory, regular_user, owner_user, db_session):
        product = product_factory(title="Cancel", price=Decimal("25"), quantity=10, seller_id=owner_user.id)
        order = order_factory(
            buyer_id=regular_user.id,
            total_price=Decimal("25"),
            items=[{
                "product_id": product.id,
                "seller_id": owner_user.id,
                "product_title": "Cancel",
                "unit_price": Decimal("25"),
                "quantity": 2,
            }],
        )
        original_quantity = product.quantity
        data = OrderStatusUpdate(status=OrderStatus.CANCELLED)
        cancelled = orders_service.update_order_status(db_session, order.id, data, regular_user)
        assert cancelled.status == OrderStatus.CANCELLED
        db_session.refresh(product)
        assert product.quantity == original_quantity + 2

    def test_cancel_order_not_pending(self, order_factory, regular_user, db_session):
        order = order_factory(buyer_id=regular_user.id, status=OrderStatus.CONFIRMED, total_price=Decimal("50"))
        data = OrderStatusUpdate(status=OrderStatus.CANCELLED)
        with pytest.raises(OrderCannotBeCancelledError):
            orders_service.update_order_status(db_session, order.id, data, regular_user)

    def test_cancel_order_not_found(self, regular_user, db_session):
        data = OrderStatusUpdate(status=OrderStatus.CANCELLED)
        with pytest.raises(OrderNotFoundError):
            orders_service.update_order_status(db_session, 99999, data, regular_user)

    def test_cancel_order_not_owner(self, order_factory, regular_user, other_user, db_session):
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50"))
        data = OrderStatusUpdate(status=OrderStatus.CANCELLED)
        with pytest.raises(ForbiddenError):
            orders_service.update_order_status(db_session, order.id, data, other_user)


# ──────────────────────────────────────────────────────────────
# Admin Service
# ──────────────────────────────────────────────────────────────


class TestAdminService:
    def test_get_all_users(self, user_factory, db_session):
        user_factory(username="a1")
        user_factory(username="a2")
        users = service.get_all_users(db_session)
        assert len(users) >= 2

    def test_get_user(self, user_factory, db_session):
        user = user_factory(username="adminfind")
        found = service.get_user(db_session, user.id)
        assert found.username == "adminfind"

    def test_get_user_not_found(self, db_session):
        with pytest.raises(UserNotFoundError):
            service.get_user(db_session, 99999)

    def test_ban_user(self, user_factory, admin_user, db_session):
        target = user_factory(username="toban")
        banned = service.ban_user(db_session, target.id, admin_user)
        assert banned.is_active is False

    def test_ban_self(self, admin_user, db_session):
        with pytest.raises(AppException) as exc_info:
            service.ban_user(db_session, admin_user.id, admin_user)
        assert exc_info.value.status_code == 400

    def test_ban_admin_by_admin(self, admin_user, user_factory, db_session):
        other_admin = user_factory(username="otheradmin", role=UserRole.ADMIN)
        with pytest.raises(AppException) as exc_info:
            service.ban_user(db_session, other_admin.id, admin_user)
        assert exc_info.value.status_code == 403

    def test_ban_owner_by_admin(self, admin_user, owner_user, db_session):
        with pytest.raises(AppException) as exc_info:
            service.ban_user(db_session, owner_user.id, admin_user)
        assert exc_info.value.status_code == 403

    def test_unban_user(self, user_factory, admin_user, db_session):
        target = user_factory(username="tounban", is_active=False)
        unbanned = service.unban_user(db_session, target.id, admin_user)
        assert unbanned.is_active is True

    def test_unban_admin_by_admin(self, admin_user, user_factory, db_session):
        other_admin = user_factory(username="bannedadmin", role=UserRole.ADMIN, is_active=False)
        with pytest.raises(AppException) as exc_info:
            service.unban_user(db_session, other_admin.id, admin_user)
        assert exc_info.value.status_code == 403

    def test_promote_to_admin(self, user_factory, owner_user, db_session):
        target = user_factory(username="topromote")
        promoted = service.promote_to_admin(db_session, target.id, owner_user)
        assert promoted.role == UserRole.ADMIN

    def test_promote_already_admin(self, user_factory, owner_user, db_session):
        target = user_factory(username="alreadyadmin", role=UserRole.ADMIN)
        with pytest.raises(AppException) as exc_info:
            service.promote_to_admin(db_session, target.id, owner_user)
        assert exc_info.value.status_code == 400

    def test_promote_already_owner(self, user_factory, owner_user, db_session):
        with pytest.raises(AppException) as exc_info:
            service.promote_to_admin(db_session, owner_user.id, owner_user)
        assert exc_info.value.status_code == 400

    def test_promote_nonexistent_user(self, owner_user, db_session):
        with pytest.raises(UserNotFoundError):
            service.promote_to_admin(db_session, 99999, owner_user)

    def test_demote_admin(self, user_factory, owner_user, db_session):
        admin = user_factory(username="todemote", role=UserRole.ADMIN)
        demoted = service.demote_to_user(db_session, admin.id, owner_user)
        assert demoted.role == UserRole.USER

    def test_demote_self(self, owner_user, db_session):
        with pytest.raises(SelfDemoteError):
            service.demote_to_user(db_session, owner_user.id, owner_user)

    def test_demote_non_admin(self, user_factory, owner_user, db_session):
        user = user_factory(username="regular")
        with pytest.raises(ForbiddenError):
            service.demote_to_user(db_session, user.id, owner_user)

    def test_demote_nonexistent_user(self, owner_user, db_session):
        with pytest.raises(UserNotFoundError):
            service.demote_to_user(db_session, 99999, owner_user)
