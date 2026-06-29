from sqlalchemy import func, select
from sqlalchemy.orm import Session
from src.products.models import Product, ProductImage
from src.products.schemas import ProductFilter, PaginationParams
from src.orders.models import OrderItem



def get_by_id(db: Session, product_id: int) -> Product | None:
    return db.get(Product, product_id)


def get_all(db: Session) -> list[Product] | None:
    query = select(Product)
    result = db.execute(query).scalars().all()

    return result


def get_filtered(db: Session, filters: ProductFilter, pagination: PaginationParams) -> tuple[list[Product], int]:
    query = select(Product)

    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.where(
            (Product.title.ilike(search_term)) |
            (Product.description.ilike(search_term))
        )

    if filters.category:
        query = query.where(Product.category == filters.category)

    if filters.min_price is not None:
        query = query.where(Product.price >= filters.min_price)

    if filters.max_price is not None:
        query = query.where(Product.price <= filters.max_price)

    if filters.min_quantity is not None:
        query = query.where(Product.quantity >= filters.min_quantity)

    if filters.max_quantity is not None:
        query = query.where(Product.quantity <= filters.max_quantity)

    if filters.is_active is not None:
        query = query.where(Product.is_active == filters.is_active)

    if filters.seller_id is not None:
        query = query.where(Product.seller_id == filters.seller_id)

    if filters.created_after is not None:
        query = query.where(Product.created_at >= filters.created_after)

    if filters.created_before is not None:
        query = query.where(Product.created_at <= filters.created_before)

    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar()

    allowed_sort_columns = {"created_at", "price", "title", "quantity"}
    sort_by = filters.sort_by if filters.sort_by in allowed_sort_columns else "created_at"
    sort_column = getattr(Product, sort_by)
    if filters.sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    offset = (pagination.page - 1) * pagination.page_size
    query = query.offset(offset).limit(pagination.page_size)

    products = db.execute(query).scalars().all()
    return list(products), total


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

def add_image(db: Session, image: ProductImage) -> ProductImage:
    db.add(image)
    db.commit()
    db.refresh(image)
    return image

def get_image_by_id(db: Session, image_id: int) -> ProductImage | None:
    return db.get(ProductImage, image_id)

def delete_image(db: Session, image: ProductImage) -> None:
    db.delete(image)
    db.commit()


def count_order_items(db: Session, product_id: int) -> int:
    query = (
        select(func.count())
        .select_from(OrderItem)
        .where(OrderItem.product_id == product_id)
    )
    return db.execute(query).scalar() or 0
