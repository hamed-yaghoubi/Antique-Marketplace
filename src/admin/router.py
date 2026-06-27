import math
from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.admin.schemas import AdminProductCreate, AdminProductUpdate
from src.core.exceptions import ProductNotFoundError
from src.dependencies.auth import CurrentUser
from src.dependencies.db import DbSession
from src.dependencies.permissions import require_admin
from src.products.schemas import (
    ProductResponse,
    PaginationParams,
    ProductFilter,
    PaginatedResponse,
)
from src.products import service
from src.products.models import Product

router = APIRouter(prefix="/admin", tags=["Admin"])


def get_admin_user(current_user: CurrentUser):
    return require_admin(current_user)


@router.get("/products", response_model=PaginatedResponse)
def list_products(
    db: DbSession,
    current_user: dict = Depends(get_admin_user),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = None,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_quantity: int | None = None,
    max_quantity: int | None = None,
    is_active: bool | None = None,
    seller_id: int | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
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
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: DbSession,
    current_user: dict = Depends(get_admin_user),
):
    try:
        return service.get_product(db, product_id)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    data: AdminProductCreate,
    db: DbSession,
    current_user: dict = Depends(get_admin_user),
):
    from src.products.models import Product

    product = Product(**data.model_dump())
    return service.repository.create(db, product)


@router.patch("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: AdminProductUpdate,
    db: DbSession,
    current_user: dict = Depends(get_admin_user),
):
    try:
        product = service.get_product(db, product_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)

        return service.repository.update(db, product)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: DbSession,
    current_user: dict = Depends(get_admin_user),
):
    try:
        product = service.get_product(db, product_id)
        service.repository.delete(db, product)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
