from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.products.category import ProductCategory
from src.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(255), index=True)

    description: Mapped[str] = mapped_column(Text)

    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), index=True)

    quantity: Mapped[int]

    category: Mapped[ProductCategory] = mapped_column(Enum(ProductCategory), index=True)

    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    is_active: Mapped[bool] = mapped_column(default=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    seller = relationship("User", back_populates="products")

    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="product", cascade="all, delete-orphan")

    images: Mapped[list["ProductImage"]] = relationship(back_populates="product", cascade="all, delete-orphan")


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    image_url: Mapped[str] = mapped_column(String(500))

    product: Mapped["Product"] = relationship(back_populates="images")