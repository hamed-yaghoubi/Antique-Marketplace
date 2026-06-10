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

    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    quantity: Mapped[int]

    category: Mapped[ProductCategory] = mapped_column(Enum(ProductCategory))

    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    seller = relationship("User", back_populates="products")

    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="product", cascade="all, delete-orphan")