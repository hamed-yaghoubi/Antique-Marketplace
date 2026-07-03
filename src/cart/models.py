from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        Index("ix_cart_items_user_product", "user_id", "product_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)

    quantity: Mapped[int]

    user = relationship("User", back_populates="cart_items")

    product = relationship("Product", back_populates="cart_items")

