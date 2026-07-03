from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.cart import repository as cart_repository
from src.orders.orderstatus import OrderStatus
from src.core.exceptions import (
    EmptyCartError,
    ForbiddenError,
    InsufficientStockError,
    InvalidOrderStatusTransition,
    OrderCannotBeCancelledError,
    OrderNotFoundError,
    SelfPurchaseError,
)
from src.orders.models import Order, OrderItem
from src.orders import repository
from src.orders.schemas import OrderFilter, OrderStatusUpdate, PaginationParams
from src.products.models import Product
from src.users.models import User
from src.users.role import UserRole

VALID_TRANSITIONS: dict[OrderStatus, list[OrderStatus]] = {
    OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
    OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
    OrderStatus.PREPARING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
    OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
    OrderStatus.DELIVERED: [],
    OrderStatus.CANCELLED: [],
}

CANCELLATION_BY_ROLE: dict[UserRole, list[OrderStatus]] = {
    UserRole.USER: [OrderStatus.PENDING],
    UserRole.OWNER: [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PREPARING],
    UserRole.ADMIN: [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PREPARING],
}


def create_order(db: Session, current_user: User) -> Order:
    cart_items = cart_repository.get_by_user_id(db, current_user.id)

    if not cart_items:
        raise EmptyCartError()

    order = Order(
        buyer_id=current_user.id,
        status=OrderStatus.PENDING,
        total_price=Decimal("0")
    )

    for cart_item in cart_items:
        product = db.execute(
            select(Product).where(Product.id == cart_item.product_id).with_for_update()
        ).scalar_one()

        if not product.is_active:
            from src.core.exceptions import ProductNotFoundError
            raise ProductNotFoundError(product.id)

        if product.seller_id == current_user.id:
            raise SelfPurchaseError()

        if cart_item.quantity > product.quantity:
            raise InsufficientStockError()

        product.quantity -= cart_item.quantity

        order_item = OrderItem(
            product_id=product.id,
            seller_id=product.seller_id,
            product_title=product.title,
            unit_price=product.price,
            quantity=cart_item.quantity
        )

        order.total_price += product.price * cart_item.quantity

        order.items.append(order_item)

    order = repository.create(db, order)
    cart_repository.clear(db, current_user.id)

    return order


def get_filtered_orders(
    db: Session,
    filters: OrderFilter,
    pagination: PaginationParams,
    current_user: User,
) -> tuple[list[Order], int]:
    seller_id = None
    if current_user.role == UserRole.OWNER:
        seller_id = current_user.id

    return repository.get_filtered(db, filters, pagination, seller_id=seller_id)


def get_orders(db: Session, current_user: User) -> list[Order]:
    if current_user.role == UserRole.OWNER:
        return repository.get_by_seller_id(db, current_user.id)
    if current_user.role == UserRole.ADMIN:
        return repository.get_all(db)
    return repository.get_by_buyer_id(db, current_user.id)


def get_order(db: Session, order_id: int, current_user: User) -> Order:
    order = repository.get_by_id(db, order_id)

    if order is None:
        raise OrderNotFoundError()

    if current_user.role == UserRole.ADMIN:
        return order

    if current_user.role == UserRole.OWNER:
        if repository.order_contains_seller_product(db, order_id, current_user.id):
            return order
        raise ForbiddenError()

    if order.buyer_id != current_user.id:
        raise ForbiddenError()

    return order


def update_order_status(db: Session, order_id: int, data: OrderStatusUpdate, current_user: User) -> Order:
    order = repository.get_by_id(db, order_id)

    if order is None:
        raise OrderNotFoundError()

    # Check role-based authorization
    if current_user.role in (UserRole.OWNER, UserRole.ADMIN):
        if current_user.role == UserRole.OWNER and not repository.order_contains_seller_product(db, order_id, current_user.id):
            raise ForbiddenError()
    elif current_user.role == UserRole.USER:
        if order.buyer_id != current_user.id:
            raise ForbiddenError()
    else:
        raise ForbiddenError()

    # Check transition validity
    allowed = VALID_TRANSITIONS.get(order.status, [])
    if data.status not in allowed:
        raise InvalidOrderStatusTransition(order.status.value, data.status.value)

    # For cancellation, enforce role-based rules
    if data.status == OrderStatus.CANCELLED:
        allowed_cancel_statuses = CANCELLATION_BY_ROLE.get(current_user.role, [])
        if order.status not in allowed_cancel_statuses:
            raise OrderCannotBeCancelledError()

    # Restore inventory on cancellation
    if data.status == OrderStatus.CANCELLED and order.status != OrderStatus.CANCELLED:
        for item in order.items:
            product = db.execute(
                select(Product).where(Product.id == item.product_id).with_for_update()
            ).scalar_one()
            product.quantity += item.quantity

    order.status = data.status

    return repository.update(db, order)


def get_order_stats(db: Session, current_user: User) -> dict:
    if current_user.role == UserRole.OWNER:
        return repository.get_order_stats(db, seller_id=current_user.id)
    if current_user.role == UserRole.USER:
        return repository.get_order_stats(db, buyer_id=current_user.id)
    return repository.get_order_stats(db)


def get_dashboard_stats(db: Session, current_user: User) -> dict:
    if current_user.role == UserRole.OWNER:
        return repository.get_dashboard_stats(db, seller_id=current_user.id)
    return repository.get_dashboard_stats(db)
