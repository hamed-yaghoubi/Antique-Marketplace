from sqlalchemy.orm import Session
from src.core.exceptions import ForbiddenError, ProductNotFoundError
from src.products.models import Product
from src.products import repository
from src.products.schemas import ProductCreate, ProductUpdate
from src.users.models import User


def get_product(db: Session, product_id: int) -> Product:
    
    product = repository.get_by_id(db, product_id)

    if product is None:
        raise ProductNotFoundError()

    return product

def get_products(db: Session) -> list[Product]:
    return repository.get_all(db)

def get_my_products(db: Session, current_user: User) -> list[Product]:
    return repository.get_by_seller_id(db, current_user.id)

def create_product(db: Session, data: ProductCreate, current_user: User) -> Product:

    product = Product(**data.model_dump(), seller_id=current_user.id)

    return repository.create(db, product)


def update_product(db: Session, product_id: int, data: ProductUpdate, current_user: User) -> Product:

    product = get_product(db, product_id)

    if product.seller_id != current_user.id:
        raise ForbiddenError()

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product, field, value)

    return repository.update(db, product)


def delete_product(db: Session, product_id: int, current_user: User) -> None:

    product = get_product(db, product_id)

    if product.seller_id != current_user.id:
        raise ForbiddenError()

    repository.delete(db, product)