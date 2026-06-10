from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from src.products.schemas import ProductCard


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    quantity: int
    product: ProductCard

    model_config = ConfigDict(from_attributes=True)

class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_price: Decimal
