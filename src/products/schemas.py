from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from src.products.category import ProductCategory
from datetime import datetime


class ProductImageResponse(BaseModel):
    id: int
    image_url: str
    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    title: str
    description: str
    price: Decimal
    quantity: int
    category: ProductCategory


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    seller_id: int
    created_at: datetime
    images: list[ProductImageResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ProductUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: Decimal | None = None
    quantity: int | None = None
    category: ProductCategory | None = None


class ProductCard(BaseModel):
    id: int
    title: str
    price: Decimal
    category: ProductCategory
    images: list[ProductImageResponse] = []

    model_config = ConfigDict(from_attributes=True)