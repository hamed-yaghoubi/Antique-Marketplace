from fastapi import UploadFile
from sqlalchemy.orm import Session
from src.core.exceptions import ForbiddenError, ProductNotFoundError
from src.products.models import Product, ProductImage
from src.products import repository
from src.products.schemas import ProductCreate, ProductUpdate, ProductFilter, PaginationParams
from src.users.models import User
import os, uuid
from src.core.config import get_settings

settings = get_settings()

def get_product(db: Session, product_id: int) -> Product:

    product = repository.get_by_id(db, product_id)

    if product is None:
        raise ProductNotFoundError()

    return product

def get_products(db: Session) -> list[Product]:
    return repository.get_all(db)

def get_filtered_products(
    db: Session,
    filters: ProductFilter,
    pagination: PaginationParams,
) -> tuple[list[Product], int]:
    return repository.get_filtered(db, filters, pagination)

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


def upload_product_image(db: Session, product_id: int, file: UploadFile, current_user: User) -> ProductImage:
    product = get_product(db, product_id)

    if product.seller_id != current_user.id:
        raise ForbiddenError()

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(file.file.read())

    image = ProductImage(
        product_id=product_id,
        image_url=f"/{settings.UPLOAD_DIR}/{filename}"
    )

    return repository.add_image(db, image)

def delete_product_image(db: Session, product_id: int, image_id: int, current_user: User) -> None:
    product = get_product(db, product_id)

    if product.seller_id != current_user.id:
        raise ForbiddenError()

    image = repository.get_image_by_id(db, image_id)

    if image is None or image.product_id != product_id:
        raise ProductNotFoundError()

    repository.delete_image(db, image)