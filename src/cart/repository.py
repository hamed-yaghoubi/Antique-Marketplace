from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from src.cart.models import CartItem


def get_by_id(db: Session, item_id: int) -> CartItem | None:
    return db.get(CartItem, item_id)


def get_by_user_id(db: Session, user_id: int) -> list[CartItem]:
    query = select(CartItem).where(CartItem.user_id == user_id)
    result = db.execute(query).scalars().all()
    return result


def get_by_user_and_product(db: Session, user_id: int, product_id: int) -> CartItem | None:
    query = select(CartItem).where(CartItem.user_id == user_id, CartItem.product_id == product_id)
    result = db.execute(query).scalar_one_or_none()
    return result

def create(db: Session, cart_item: CartItem) -> CartItem:
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)

    return cart_item


def update(db: Session, cart_item: CartItem) -> CartItem:
    db.commit()
    db.refresh(cart_item)

    return cart_item


def delete_item(db: Session, cart_item: CartItem) -> None:
    db.delete(cart_item)
    db.commit()


def clear(db: Session, user_id: int) -> None:
    query = delete(CartItem).where(CartItem.user_id == user_id)
    db.execute(query)
    db.commit()