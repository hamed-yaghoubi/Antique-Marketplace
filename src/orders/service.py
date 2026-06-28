from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.cart import repository as cart_repository
from src.orders.orderstatus import OrderStatus
from src.core.exceptions import InsufficientStockError, ForbiddenError, OrderNotFoundError
from src.orders.models import Order, OrderItem
from src.orders import repository
from src.orders.schemas import OrderStatusUpdate
from src.products.models import Product
from src.users.models import User


def create_order(db: Session, current_user: User) -> Order:
    cart_items = cart_repository.get_by_user_id(db, current_user.id)

    if not cart_items:
        from src.core.exceptions import EmptyCartError
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


def get_orders(db: Session, current_user: User) -> list[Order]:
    return repository.get_by_buyer_id(db, current_user.id)


def get_order(db: Session, order_id: int, current_user: User) -> Order:
    order = repository.get_by_id(db, order_id)

    if order is None:
        raise OrderNotFoundError()

    if order.buyer_id != current_user.id:
        raise ForbiddenError()

    return order


def cancel_order(db: Session, order_id: int, data: OrderStatusUpdate, current_user: User) -> Order:
    order = repository.get_by_id(db, order_id)

    if order is None:
        raise OrderNotFoundError()

    if order.buyer_id != current_user.id:
        raise ForbiddenError()

    if order.status != OrderStatus.PENDING:
        from src.core.exceptions import OrderCannotBeCancelledError
        raise OrderCannotBeCancelledError()

    for item in order.items:
        product = db.execute(
            select(Product).where(Product.id == item.product_id).with_for_update()
        ).scalar_one()
        product.quantity += item.quantity

    order.status = data.status

    return repository.update(db, order)