"""Repository layer tests — CRUD operations and edge cases."""
from decimal import Decimal
from datetime import datetime, timedelta, UTC

import pytest
from sqlalchemy.exc import IntegrityError

from src.core import security
from src.users.models import User
from src.users.role import UserRole
from src.users import repository
from src.products.models import Product, ProductImage
from src.products.category import ProductCategory
from src.products import repository as products_repo
from src.products.schemas import ProductFilter, PaginationParams
from src.cart.models import CartItem
from src.cart import repository as cart_repo
from src.orders.models import Order, OrderItem
from src.orders.orderstatus import OrderStatus
from src.orders import repository as orders_repo



# ──────────────────────────────────────────────────────────────
# Users Repository
# ──────────────────────────────────────────────────────────────


class TestUsersRepository:
    def test_get_by_id(self, user_factory, db_session):
        user = user_factory(username="findme")
        found = repository.get_by_id(db_session, user.id)
        assert found is not None
        assert found.username == "findme"

    def test_get_by_id_not_found(self, db_session):
        found = repository.get_by_id(db_session, 99999)
        assert found is None

    def test_get_by_username(self, user_factory, db_session):
        user = user_factory(username="byusername")
        found = repository.get_by_username(db_session, "byusername")
        assert found is not None
        assert found.id == user.id

    def test_get_by_username_not_found(self, db_session):
        found = repository.get_by_username(db_session, "nobody")
        assert found is None

    def test_create_user(self, db_session):
        user = User(
            username="newuser",
            hashed_password=security.hash_password("pass"),
            role=UserRole.USER,
        )
        created = repository.create(db_session, user)
        assert created.id is not None
        assert created.username == "newuser"

    def test_create_duplicate_username(self, user_factory, db_session):
        user_factory(username="dupe")
        with pytest.raises(IntegrityError):
            user_factory(username="dupe")

    def test_update_user(self, user_factory, db_session):
        user = user_factory(username="before")
        user.username = "after"
        updated = repository.update(db_session, user)
        assert updated.username == "after"

    def test_delete_user(self, user_factory, db_session):
        user = user_factory(username="deleteme")
        repository.delete(db_session, user)
        assert repository.get_by_id(db_session, user.id) is None


# ──────────────────────────────────────────────────────────────
# Products Repository
# ──────────────────────────────────────────────────────────────


class TestProductsRepository:
    def test_get_by_id(self, product_factory, owner_user, db_session):
        product = product_factory(title="Find Me", seller_id=owner_user.id)
        found = products_repo.get_by_id(db_session, product.id)
        assert found is not None
        assert found.title == "Find Me"

    def test_get_by_id_not_found(self, db_session):
        assert products_repo.get_by_id(db_session, 99999) is None

    def test_get_all(self, product_factory, owner_user, db_session):
        product_factory(title="P1", seller_id=owner_user.id)
        product_factory(title="P2", seller_id=owner_user.id)
        products = products_repo.get_all(db_session)
        assert len(products) >= 2

    def test_create_product(self, owner_user, db_session):
        product = Product(
            title="New",
            description="Desc",
            price=Decimal("10.00"),
            quantity=5,
            category=ProductCategory.COIN,
            seller_id=owner_user.id,
        )
        created = products_repo.create(db_session, product)
        assert created.id is not None

    def test_update_product(self, product_factory, owner_user, db_session):
        product = product_factory(title="Old", seller_id=owner_user.id)
        product.title = "New"
        updated = products_repo.update(db_session, product)
        assert updated.title == "New"

    def test_delete_product(self, product_factory, owner_user, db_session):
        product = product_factory(title="Delete Me", seller_id=owner_user.id)
        products_repo.delete(db_session, product)
        assert products_repo.get_by_id(db_session, product.id) is None

    def test_get_by_seller_id(self, product_factory, owner_user, db_session):
        product_factory(title="Seller1", seller_id=owner_user.id)
        result = products_repo.get_by_seller_id(db_session, owner_user.id)
        assert len(result) >= 1
        assert all(p.seller_id == owner_user.id for p in result)

    def test_get_by_seller_id_empty(self, db_session):
        result = products_repo.get_by_seller_id(db_session, 99999)
        assert result == []

    def test_add_image(self, product_factory, owner_user, db_session):
        product = product_factory(seller_id=owner_user.id)
        image = ProductImage(product_id=product.id, image_url="/img.jpg")
        added = products_repo.add_image(db_session, image)
        assert added.id is not None
        assert added.image_url == "/img.jpg"

    def test_get_image_by_id(self, product_factory, owner_user, db_session):
        product = product_factory(seller_id=owner_user.id)
        image = ProductImage(product_id=product.id, image_url="/img.jpg")
        products_repo.add_image(db_session, image)
        found = products_repo.get_image_by_id(db_session, image.id)
        assert found is not None

    def test_get_image_by_id_not_found(self, db_session):
        assert products_repo.get_image_by_id(db_session, 99999) is None

    def test_delete_image(self, product_factory, owner_user, db_session):
        product = product_factory(seller_id=owner_user.id)
        image = ProductImage(product_id=product.id, image_url="/img.jpg")
        products_repo.add_image(db_session, image)
        products_repo.delete_image(db_session, image)
        assert products_repo.get_image_by_id(db_session, image.id) is None

    def test_count_order_items_zero(self, product_factory, owner_user, db_session):
        product = product_factory(seller_id=owner_user.id)
        count = products_repo.count_order_items(db_session, product.id)
        assert count == 0


class TestProductFiltering:
    def _create_products(self, product_factory, owner_user, db_session):
        products = []
        data = [
            ("Antique Coin", ProductCategory.COIN, Decimal("50.00"), 10),
            ("Grandfather Clock", ProductCategory.CLOCK, Decimal("250.00"), 3),
            ("Oil Painting", ProductCategory.PAINTING, Decimal("500.00"), 1),
            ("Old Book", ProductCategory.BOOK, Decimal("25.00"), 20),
            ("Marble Statue", ProductCategory.STATUE, Decimal("1000.00"), 0),
        ]
        for title, cat, price, qty in data:
            p = product_factory(
                title=title, category=cat, price=price,
                quantity=qty, seller_id=owner_user.id,
            )
            products.append(p)
        return products

    def test_filter_by_category(self, product_factory, owner_user, db_session):
        self._create_products(product_factory, owner_user, db_session)
        filters = ProductFilter(category=ProductCategory.COIN)
        pagination = PaginationParams(page=1, page_size=20)
        products, total = products_repo.get_filtered(db_session, filters, pagination)
        assert all(p.category == ProductCategory.COIN for p in products)
        assert total >= 1

    def test_filter_by_price_range(self, product_factory, owner_user, db_session):
        self._create_products(product_factory, owner_user, db_session)
        filters = ProductFilter(min_price=Decimal("100"), max_price=Decimal("300"))
        pagination = PaginationParams(page=1, page_size=20)
        products, total = products_repo.get_filtered(db_session, filters, pagination)
        assert all(Decimal("100") <= p.price <= Decimal("300") for p in products)

    def test_filter_by_search(self, product_factory, owner_user, db_session):
        self._create_products(product_factory, owner_user, db_session)
        filters = ProductFilter(search="Coin")
        pagination = PaginationParams(page=1, page_size=20)
        products, total = products_repo.get_filtered(db_session, filters, pagination)
        assert len(products) >= 1
        assert any("Coin" in p.title for p in products)

    def test_filter_by_seller(self, product_factory, owner_user, other_user, db_session):
        self._create_products(product_factory, owner_user, db_session)
        product_factory(title="Other's", seller_id=other_user.id, price=Decimal("10"))
        filters = ProductFilter(seller_id=owner_user.id)
        pagination = PaginationParams(page=1, page_size=20)
        products, total = products_repo.get_filtered(db_session, filters, pagination)
        assert all(p.seller_id == owner_user.id for p in products)

    def test_filter_by_active_status(self, product_factory, owner_user, db_session):
        product_factory(title="Active", seller_id=owner_user.id, is_active=True)
        product_factory(title="Inactive", seller_id=owner_user.id, is_active=False)
        filters = ProductFilter(is_active=False)
        pagination = PaginationParams(page=1, page_size=20)
        products, total = products_repo.get_filtered(db_session, filters, pagination)
        assert all(not p.is_active for p in products)

    def test_filter_by_quantity_range(self, product_factory, owner_user, db_session):
        self._create_products(product_factory, owner_user, db_session)
        filters = ProductFilter(min_quantity=5, max_quantity=15)
        pagination = PaginationParams(page=1, page_size=20)
        products, total = products_repo.get_filtered(db_session, filters, pagination)
        assert all(5 <= p.quantity <= 15 for p in products)

    def test_pagination(self, product_factory, owner_user, db_session):
        for i in range(25):
            product_factory(title=f"Item {i}", seller_id=owner_user.id, price=Decimal(str(i)))
        filters = ProductFilter()
        pagination = PaginationParams(page=1, page_size=10)
        products, total = products_repo.get_filtered(db_session, filters, pagination)
        assert len(products) == 10
        assert total >= 25

    def test_sort_by_price_asc(self, product_factory, owner_user, db_session):
        self._create_products(product_factory, owner_user, db_session)
        filters = ProductFilter(sort_by="price", sort_order="asc")
        pagination = PaginationParams(page=1, page_size=20)
        products, total = products_repo.get_filtered(db_session, filters, pagination)
        prices = [p.price for p in products]
        assert prices == sorted(prices)

    def test_invalid_sort_column_falls_back(self, product_factory, owner_user, db_session):
        self._create_products(product_factory, owner_user, db_session)
        filters = ProductFilter(sort_by="invalid_column", sort_order="desc")
        pagination = PaginationParams(page=1, page_size=20)
        products, total = products_repo.get_filtered(db_session, filters, pagination)
        assert len(products) >= 1


# ──────────────────────────────────────────────────────────────
# Cart Repository
# ──────────────────────────────────────────────────────────────


class TestCartRepository:
    def test_get_by_id(self, cart_item_factory, regular_user, sample_product, db_session):
        item = cart_item_factory(user_id=regular_user.id, product_id=sample_product.id)
        found = cart_repo.get_by_id(db_session, item.id)
        assert found is not None

    def test_get_by_id_not_found(self, db_session):
        assert cart_repo.get_by_id(db_session, 99999) is None

    def test_get_by_user_id(self, cart_item_factory, regular_user, sample_product, db_session):
        cart_item_factory(user_id=regular_user.id, product_id=sample_product.id)
        items = cart_repo.get_by_user_id(db_session, regular_user.id)
        assert len(items) >= 1
        assert items[0].product is not None

    def test_get_by_user_id_empty(self, db_session):
        items = cart_repo.get_by_user_id(db_session, 99999)
        assert items == []

    def test_get_by_user_and_product(self, cart_item_factory, regular_user, sample_product, db_session):
        cart_item_factory(user_id=regular_user.id, product_id=sample_product.id)
        found = cart_repo.get_by_user_and_product(db_session, regular_user.id, sample_product.id)
        assert found is not None

    def test_get_by_user_and_product_not_found(self, regular_user, sample_product, db_session):
        found = cart_repo.get_by_user_and_product(db_session, regular_user.id, sample_product.id)
        assert found is None

    def test_create_cart_item(self, regular_user, sample_product, db_session):
        item = CartItem(user_id=regular_user.id, product_id=sample_product.id, quantity=2)
        created = cart_repo.create(db_session, item)
        assert created.id is not None
        assert created.quantity == 2

    def test_update_cart_item(self, cart_item_factory, regular_user, sample_product, db_session):
        item = cart_item_factory(user_id=regular_user.id, product_id=sample_product.id)
        item.quantity = 5
        updated = cart_repo.update(db_session, item)
        assert updated.quantity == 5

    def test_delete_cart_item(self, cart_item_factory, regular_user, sample_product, db_session):
        item = cart_item_factory(user_id=regular_user.id, product_id=sample_product.id)
        cart_repo.delete_item(db_session, item)
        assert cart_repo.get_by_id(db_session, item.id) is None

    def test_clear_cart(self, cart_item_factory, regular_user, sample_product, db_session):
        cart_item_factory(user_id=regular_user.id, product_id=sample_product.id)
        cart_repo.clear(db_session, regular_user.id)
        items = cart_repo.get_by_user_id(db_session, regular_user.id)
        assert items == []


# ──────────────────────────────────────────────────────────────
# Orders Repository
# ──────────────────────────────────────────────────────────────


class TestOrdersRepository:
    def test_get_by_id(self, order_factory, regular_user, db_session):
        order = order_factory(buyer_id=regular_user.id, total_price=Decimal("50.00"))
        found = orders_repo.get_by_id(db_session, order.id)
        assert found is not None

    def test_get_by_id_not_found(self, db_session):
        assert orders_repo.get_by_id(db_session, 99999) is None

    def test_get_by_buyer_id(self, order_factory, regular_user, db_session):
        order_factory(buyer_id=regular_user.id, total_price=Decimal("50.00"))
        order_factory(buyer_id=regular_user.id, total_price=Decimal("100.00"))
        orders = orders_repo.get_by_buyer_id(db_session, regular_user.id)
        assert len(orders) >= 2

    def test_get_by_buyer_id_empty(self, db_session):
        orders = orders_repo.get_by_buyer_id(db_session, 99999)
        assert orders == []

    def test_create_order(self, regular_user, db_session):
        order = Order(
            buyer_id=regular_user.id,
            status=OrderStatus.PENDING,
            total_price=Decimal("75.00"),
        )
        created = orders_repo.create(db_session, order)
        assert created.id is not None
        assert created.total_price == Decimal("75.00")

    def test_update_order(self, order_factory, regular_user, db_session):
        order = order_factory(buyer_id=regular_user.id)
        order.status = OrderStatus.CONFIRMED
        updated = orders_repo.update(db_session, order)
        assert updated.status == OrderStatus.CONFIRMED


# ──────────────────────────────────────────────────────────────
# Admin Repository
# ──────────────────────────────────────────────────────────────


class TestAdminRepository:
    def test_get_all_users(self, user_factory, db_session):
        user_factory(username="u1")
        user_factory(username="u2")
        users = repository.get_all_users(db_session)
        assert len(users) >= 2

    def test_get_by_id(self, user_factory, db_session):
        user = user_factory(username="adminfind")
        found = repository.get_by_id(db_session, user.id)
        assert found is not None

    def test_get_by_id_not_found(self, db_session):
        assert repository.get_by_id(db_session, 99999) is None

    def test_update(self, user_factory, db_session):
        user = user_factory(username="before")
        user.username = "after"
        updated = repository.update(db_session, user)
        assert updated.username == "after"
