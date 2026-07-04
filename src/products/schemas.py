from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from src.products.category import ProductCategory
from datetime import datetime


class ProductImageResponse(BaseModel):
    id: int
    image_url: str
    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=10000)
    price: Decimal = Field(gt=0, le=99999999.99)
    quantity: int = Field(ge=0, le=999999)
    category: ProductCategory

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Description cannot be empty")
        return v


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
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1, max_length=10000)
    price: Decimal | None = Field(default=None, gt=0, le=99999999.99)
    quantity: int | None = Field(default=None, ge=0, le=999999)
    category: ProductCategory | None = None
    is_active: bool | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Description cannot be empty")
        return v


class ProductCard(BaseModel):
    id: int
    title: str
    price: Decimal
    category: ProductCategory
    is_active: bool
    quantity: int
    seller_id: int
    seller: str | None = None
    main_image: ProductImageResponse | None = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def extract_main_image(cls, data):
        if isinstance(data, dict):
            images = data.get("images") or []
            data["main_image"] = images[0] if images else None
            seller_user = data.get("seller")
            if isinstance(seller_user, str):
                # Already a username string — keep as-is.
                pass
            elif seller_user is not None:
                # ORM object or similar — extract its username, defaulting to
                # None when the attribute is missing instead of overwriting a
                # valid value with None.
                data["seller"] = getattr(seller_user, "username", None)
            return data

        # ORM-object path
        images = getattr(data, "images", None) or []
        seller_user = getattr(data, "seller", None)
        result = {}
        for key in ["id", "title", "price", "category", "is_active", "quantity", "seller_id"]:
            result[key] = getattr(data, key)
        result["seller"] = getattr(seller_user, "username", None) if seller_user is not None else None
        result["main_image"] = images[0] if images else None
        return result


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
