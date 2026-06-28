class AppException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UserAlreadyExistsError(AppException):
    def __init__(self):
        super().__init__("User already exists")


class UserNotFoundError(AppException):
    def __init__(self):
        super().__init__("User not found")


class InvalidCredentialsError(AppException):
    def __init__(self):
        super().__init__("Invalid credentials")


class ProductNotFoundError(AppException):
    def __init__(self):
        super().__init__("Product not found")


class CartItemNotFoundError(AppException):
    def __init__(self):
        super().__init__("Cart item not found")


class OrderNotFoundError(AppException):
    def __init__(self):
        super().__init__("Order not found")


class EmptyCartError(AppException):
    def __init__(self):
        super().__init__("Cart is empty")


class InsufficientStockError(AppException):
    def __init__(self):
        super().__init__("Insufficient stock")


class ForbiddenError(AppException):
    def __init__(self):
        super().__init__("You do not have permission to perform this action")


class OrderCannotBeCancelledError(AppException):
    def __init__(self):
        super().__init__("This order cannot be cancelled")