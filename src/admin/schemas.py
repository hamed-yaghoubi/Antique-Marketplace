from decimal import Decimal
from pydantic import BaseModel
from src.products.category import ProductCategory


class AdminProductCreate(BaseModel):
    title: str
    description: str
    sku: str
    price: Decimal
    quantity: int
    category: ProductCategory
    seller_id: int
    is_active: bool = True


class AdminProductUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    sku: str | None = None
    price: Decimal | None = None
    quantity: int | None = None
    category: ProductCategory | None = None
    seller_id: int | None = None
    is_active: bool | None = None
