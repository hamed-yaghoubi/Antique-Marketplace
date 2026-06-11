from sqlalchemy import select
from sqlalchemy.orm import Session
from src.orders.models import Order


def get_by_id(db: Session, order_id: int) -> Order | None:
    return db.get(Order, order_id)


def get_by_buyer_id(db: Session, buyer_id: int) -> list[Order]:
    query = select(Order).where(Order.buyer_id == buyer_id)
    result = db.execute(query).scalars().all()

    return result

def create(db: Session, order: Order) -> Order:
    db.add(order)
    db.commit()
    db.refresh(order)

    return order


def update(db: Session, order: Order) -> Order:
    db.commit()
    db.refresh(order)

    return order