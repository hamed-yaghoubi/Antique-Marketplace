from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from src.products.schemas import ProductCard


class CartItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=9999)

class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1, le=9999)

class CartItemResponse(BaseModel):
    id: int
    quantity: int
    product: ProductCard

    model_config = ConfigDict(from_attributes=True)

class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_price: Decimal
