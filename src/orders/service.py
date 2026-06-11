from decimal import Decimal
from sqlalchemy.orm import Session
from src.cart import repository as cart_repository
from src.orders.orderstatus import OrderStatus
from src.core.exceptions import InsufficientStockError, OrderNotFoundError
from src.orders.models import Order, OrderItem
from src.orders import repository
from src.orders.schemas import OrderStatusUpdate
from src.users.models import User


def create_order(db: Session, current_user: User) -> Order:
    cart_items = cart_repository.get_by_user_id(db, current_user.id)

    total_price = Decimal("0")

    order = Order(
        buyer_id=current_user.id,
        status=OrderStatus.PENDING,
        total_price=0
    )

    for cart_item in cart_items:
        product = cart_item.product

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

        total_price += product.price * cart_item.quantity

        order.items.append(order_item)

    order.total_price = total_price

    order = repository.create(db, order)

    cart_repository.clear(db, current_user.id)

    return order


def get_orders(db: Session, current_user: User) -> list[Order]:
    return repository.get_by_buyer_id(db, current_user.id)


def get_order(db: Session, order_id: int, current_user: User) -> Order:
    order = repository.get_by_id(db, order_id)

    if order is None:
        raise OrderNotFoundError()

    return order


def update_order_status(db: Session, order_id: int, data: OrderStatusUpdate) -> Order:
    order = repository.get_by_id(db, order_id)

    if order is None:
        raise OrderNotFoundError()

    order.status = data.status

    return repository.update(db, order)