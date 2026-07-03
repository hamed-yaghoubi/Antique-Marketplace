from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from src.core.exceptions import (
    FileTypeNotAllowedError,
    FileTooLargeError,
    ForbiddenError,
    ProductNotFoundError,
)
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

    order_item_count = repository.count_order_items(db, product_id)

    if order_item_count > 0:
        from src.core.exceptions import ProductInUseError
        raise ProductInUseError(order_item_count)

    repository.delete(db, product)


def admin_delete_product(db: Session, product_id: int, current_admin: User) -> None:
    from src.core.exceptions import ForbiddenError, AuthorizationError
    from src.users import repository as users_repository
    from src.users.role import UserRole

    product = get_product(db, product_id)

    if current_admin.role == UserRole.ADMIN:
        seller = users_repository.get_by_id(db, product.seller_id)
        if seller and seller.role in (UserRole.ADMIN, UserRole.OWNER):
            raise AuthorizationError("Admins cannot delete products belonging to admins or owners")

    order_item_count = repository.count_order_items(db, product_id)

    if order_item_count > 0:
        from src.core.exceptions import ProductInUseError
        raise ProductInUseError(order_item_count)

    repository.delete(db, product)


def upload_product_image(db: Session, product_id: int, file: UploadFile, current_user: User) -> ProductImage:
    product = get_product(db, product_id)

    if product.seller_id != current_user.id:
        raise ForbiddenError()

    allowed_exts = settings.allowed_image_extensions_set
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed_exts:
        raise FileTypeNotAllowedError(ext, list(allowed_exts))

    content = file.file.read()
    if len(content) > settings.MAX_IMAGE_SIZE:
        raise FileTooLargeError(settings.MAX_IMAGE_SIZE // (1024 * 1024))

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Sanitize filename to prevent path traversal
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    image = ProductImage(
        product_id=product_id,
        image_url=f"/{settings.UPLOAD_DIR.rstrip('/')}/{filename}"
    )

    return repository.add_image(db, image)

def delete_product_image(db: Session, product_id: int, image_id: int, current_user: User) -> None:
    product = get_product(db, product_id)

    if product.seller_id != current_user.id:
        raise ForbiddenError()

    image = repository.get_image_by_id(db, image_id)

    if image is None or image.product_id != product_id:
        raise ProductNotFoundError()

    # Delete file from disk before deleting from database
    filepath = os.path.join(".", image.image_url.lstrip("/"))
    if os.path.exists(filepath):
        os.remove(filepath)

    repository.delete_image(db, image)
