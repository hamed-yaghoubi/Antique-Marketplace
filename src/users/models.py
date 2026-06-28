from datetime import datetime
from sqlalchemy import Enum, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base
from src.users.role import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    hashed_password: Mapped[str] = mapped_column(String(255))

    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)

    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    products: Mapped[list["Product"]] = relationship(back_populates="seller", cascade="all, delete-orphan")

    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    orders: Mapped[list["Order"]] = relationship(back_populates="buyer")