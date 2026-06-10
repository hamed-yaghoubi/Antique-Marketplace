from sqlalchemy import select
from sqlalchemy.orm import Session
from src.products.models import Product


def get_by_id(db: Session, product_id: int) -> Product | None:
    return db.get(Product, product_id)


def get_all(db: Session) -> list[Product] | None:
    query = select(Product)
    result = db.execute(query).scalars().all()

    return result


def create(db: Session, product: Product) -> Product:
    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def update(db: Session, product: Product) -> Product:
    db.commit()
    db.refresh(product)

    return product


def delete(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()


def get_by_seller_id(db: Session, seller_id: int) -> list[Product] | None:
    query = select(Product).where(Product.seller_id == seller_id)
    result = db.execute(query).scalars().all()
    return result