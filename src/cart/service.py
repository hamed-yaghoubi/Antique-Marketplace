from decimal import Decimal
from sqlalchemy.orm import Session
from src.cart.models import CartItem
from src.cart import repository
from src.cart.schemas import CartItemCreate, CartItemUpdate, CartResponse
from src.core.exceptions import CartItemNotFoundError, ForbiddenError, InsufficientStockError, ProductNotFoundError
from src.products.repository import get_by_id as get_product_by_id
from src.users.models import User


def get_cart(db: Session, current_user: User) -> CartResponse:

    items = repository.get_by_user_id(db, current_user.id)

    total_price = sum(
        item.quantity * item.product.price
        for item in items
    )

    return CartResponse(
        items=items,
        total_price=Decimal(total_price)
    )


def add_item(db: Session, data: CartItemCreate, current_user: User) -> CartItem:

    product = get_product_by_id(db, data.product_id)

    if product is None:
        raise ProductNotFoundError()

    if data.quantity > product.quantity:
        raise InsufficientStockError()

    cart_item = repository.get_by_user_and_product(db, current_user.id, data.product_id)

    if cart_item:

        new_quantity = (cart_item.quantity + data.quantity)

        if new_quantity > product.quantity:
            raise InsufficientStockError()

        cart_item.quantity = new_quantity

        return repository.update(db, cart_item)

    cart_item = CartItem(
        user_id=current_user.id,
        product_id=data.product_id,
        quantity=data.quantity
    )

    return repository.create(db, cart_item)


def update_item_quantity(db: Session, item_id: int, data: CartItemUpdate, current_user: User) -> CartItem:

    cart_item = repository.get_by_id(db, item_id)

    if cart_item is None:
        raise CartItemNotFoundError()

    if cart_item.user_id != current_user.id:
        raise ForbiddenError()

    product = cart_item.product

    if data.quantity > product.quantity:
        raise InsufficientStockError()

    cart_item.quantity = data.quantity

    return repository.update(db, cart_item)


def remove_item(db: Session, item_id: int, current_user: User) -> None:

    cart_item = repository.get_by_id(db, item_id)

    if cart_item is None:
        raise CartItemNotFoundError()

    if cart_item.user_id != current_user.id:
        raise ForbiddenError()

    repository.delete_item(db, cart_item)


def clear_cart(db: Session, current_user: User) -> None:
    
    repository.clear(db, current_user.id)