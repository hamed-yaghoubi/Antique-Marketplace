import math
from fastapi import APIRouter, Query, status, UploadFile, File
from src.dependencies.auth import CurrentUser
from src.dependencies.db import DbSession
from src.products.schemas import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    ProductCard,
    ProductImageResponse,
    PaginationParams,
    ProductFilter,
    PaginatedResponse,
)
from src.products import service

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=PaginatedResponse)
def read_products(db: DbSession, page: int = Query(default=1, ge=1), page_size: int = Query(default=20, ge=1, le=100), search: str | None = None, category: str | None = None, min_price: float | None = None, max_price: float | None = None, min_quantity: int | None = None, max_quantity: int | None = None, is_active: bool | None = None, seller_id: int | None = None, sort_by: str = "created_at", sort_order: str = "desc"):
    pagination = PaginationParams(page=page, page_size=page_size)
    filters = ProductFilter(
        search=search,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_quantity=min_quantity,
        max_quantity=max_quantity,
        is_active=is_active,
        seller_id=seller_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    products, total = service.get_filtered_products(db, filters, pagination)
    total_pages = math.ceil(total / pagination.page_size) if total > 0 else 0

    return PaginatedResponse(
        items=[ProductCard.model_validate(p) for p in products],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


@router.get("/me", response_model=list[ProductCard])
def read_my_products(db: DbSession, current_user: CurrentUser):
    return service.get_my_products(db, current_user)


@router.post("/{product_id}/images", response_model=ProductImageResponse, status_code=status.HTTP_201_CREATED)
def upload_product_image(product_id: int, db: DbSession, current_user: CurrentUser, file: UploadFile = File()):
    return service.upload_product_image(db, product_id, file, current_user)


@router.delete("/{product_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_image(product_id: int, image_id: int, db: DbSession, current_user: CurrentUser):
    service.delete_product_image(db, product_id, image_id, current_user)


@router.get("/{product_id}", response_model=ProductResponse)
def read_product(product_id: int, db: DbSession):
    return service.get_product(db, product_id)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_new_product(data: ProductCreate, db: DbSession, current_user: CurrentUser):
    return service.create_product(db, data, current_user)


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, data: ProductUpdate, db: DbSession, current_user: CurrentUser):
    return service.update_product(db, product_id, data, current_user)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: DbSession, current_user: CurrentUser):
    service.delete_product(db, product_id, current_user)
