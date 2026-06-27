from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.products.category import ProductCategory
from datetime import datetime


class ProductImageResponse(BaseModel):
    id: int
    image_url: str
    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    title: str
    description: str
    sku: str
    price: Decimal
    quantity: int
    category: ProductCategory


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    seller_id: int
    is_active: bool
    created_at: datetime
    images: list[ProductImageResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ProductUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    sku: str | None = None
    price: Decimal | None = None
    quantity: int | None = None
    category: ProductCategory | None = None
    is_active: bool | None = None


class ProductCard(BaseModel):
    id: int
    title: str
    sku: str
    price: Decimal
    category: ProductCategory
    is_active: bool
    main_image: ProductImageResponse | None = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def extract_main_image(cls, data):
        images = data.get("images", [])
        if isinstance(images, list) and images:
            data["main_image"] = images[0]
        else:
            data["main_image"] = None
        return data


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class ProductFilter(BaseModel):
    search: str | None = None
    category: ProductCategory | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    min_quantity: int | None = None
    max_quantity: int | None = None
    is_active: bool | None = None
    seller_id: int | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
    sort_by: str = "created_at"
    sort_order: str = "desc"


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int