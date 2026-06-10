class AppError(Exception):
    """Base exception for all application errors."""

    default_message = "Application error"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message

        super().__init__(self.message)


# ============================================================================
# Auth
# ============================================================================

class InvalidCredentialsError(AppError):
    default_message = "Invalid password"


class UserAlreadyExistsError(AppError):
    default_message = "User already exists"


class InactiveUserError(AppError):
    default_message = "User account is inactive"


class UnauthorizedError(AppError):
    default_message = "Authentication required"


class ForbiddenError(AppError):
    default_message = "Permission denied"


# ============================================================================
# Users
# ============================================================================

class UserNotFoundError(AppError):
    default_message = "User not found"


# ============================================================================
# Products
# ============================================================================

class ProductNotFoundError(AppError):
    default_message = "Product not found"


class ProductOutOfStockError(AppError):
    default_message = "Product is out of stock"


class InvalidProductPriceError(AppError):
    default_message = "Invalid product price"


# ============================================================================
# Cart
# ============================================================================

class CartIsEmptyError(AppError):
    default_message = "Cart is empty"


class CartItemNotFoundError(AppError):
    default_message = "Cart item not found"


# ============================================================================
# Orders
# ============================================================================

class OrderNotFoundError(AppError):
    default_message = "Order not found"


class InvalidOrderStatusError(AppError):
    default_message = "Invalid order status"


class OrderAlreadyPaidError(AppError):
    default_message = "Order has already been paid"


class OrderAlreadyCancelledError(AppError):
    default_message = "Order has already been cancelled"