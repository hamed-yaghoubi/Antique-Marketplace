from fastapi import APIRouter, HTTPException, status
from src.core.exceptions import ForbiddenError, ProductNotFoundError
from src.dependencies.auth import CurrentUser
from src.dependencies.db import DbSession
from src.products.schemas import ProductCreate, ProductResponse, ProductUpdate, ProductCard
from src.products import service

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=list[ProductCard])
def read_products(db: DbSession):
    return service.get_products(db)

@router.get("/{product_id}", response_model=ProductResponse)
def read_product(product_id: int, db: DbSession):
    try:
        return service.get_product(db, product_id)

    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )

@router.post("/", response_model=ProductResponse)
def create_new_product(data: ProductCreate, db: DbSession, current_user: CurrentUser):
    return service.create_product(db, data, current_user)

@router.get("/me", response_model=list[ProductCard])
def read_my_products(db: DbSession, current_user: CurrentUser):
    return service.get_my_products(db, current_user)

@router.patch("/{product_id}", response_model=ProductResponse)
def update_product_route(product_id: int, data: ProductUpdate, db: DbSession, current_user: CurrentUser):
    try:
        return service.update_product(db, product_id, data, current_user)

    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )

    except ForbiddenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_route(product_id: int, db: DbSession, current_user: CurrentUser):
    try:
        service.delete_product(db, product_id, current_user)

    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )

    except ForbiddenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )