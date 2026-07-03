from typing import Any, Optional


class AppException(Exception):
    """Base application exception. Services and repositories raise this."""

    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        status_code: int = 400,
        details: Optional[Any] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(message)


# --- Authentication & Authorization ---


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message=message, code="AUTHENTICATION_ERROR", status_code=401)


class InvalidCredentialsError(AuthenticationError):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message=message)
        self.code = "INVALID_CREDENTIALS"


class TokenExpiredError(AuthenticationError):
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message=message)
        self.code = "TOKEN_EXPIRED"


class InvalidTokenError(AuthenticationError):
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message=message)
        self.code = "INVALID_TOKEN"


class AuthorizationError(AppException):
    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(message=message, code="AUTHORIZATION_ERROR", status_code=403)


class ForbiddenError(AuthorizationError):
    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(message=message)
        self.code = "FORBIDDEN"


class BannedAccountError(AuthorizationError):
    def __init__(self, message: str = "Your account has been banned"):
        super().__init__(message=message)
        self.code = "BANNED_ACCOUNT"


# --- Resource Errors ---


class ResourceNotFoundError(AppException):
    def __init__(self, resource: str = "Resource", resource_id: Any = None):
        message = f"{resource} not found"
        if resource_id is not None:
            message = f"{resource} with id '{resource_id}' not found"
        super().__init__(message=message, code="RESOURCE_NOT_FOUND", status_code=404)


class UserNotFoundError(ResourceNotFoundError):
    def __init__(self, user_id: Any = None):
        super().__init__(resource="User", resource_id=user_id)
        self.code = "USER_NOT_FOUND"


class ProductNotFoundError(ResourceNotFoundError):
    def __init__(self, product_id: Any = None):
        super().__init__(resource="Product", resource_id=product_id)
        self.code = "PRODUCT_NOT_FOUND"


class CartItemNotFoundError(ResourceNotFoundError):
    def __init__(self, item_id: Any = None):
        super().__init__(resource="Cart item", resource_id=item_id)
        self.code = "CART_ITEM_NOT_FOUND"


class OrderNotFoundError(ResourceNotFoundError):
    def __init__(self, order_id: Any = None):
        super().__init__(resource="Order", resource_id=order_id)
        self.code = "ORDER_NOT_FOUND"


# --- Conflict Errors ---


class ConflictError(AppException):
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message=message, code="CONFLICT", status_code=409)


class UserAlreadyExistsError(ConflictError):
    def __init__(self, message: str = "User already exists"):
        super().__init__(message=message)
        self.code = "USER_ALREADY_EXISTS"


# --- Business Rule Violations ---


class BusinessRuleViolationError(AppException):
    def __init__(self, message: str, code: str = "BUSINESS_RULE_VIOLATION"):
        super().__init__(message=message, code=code, status_code=400)


class EmptyCartError(BusinessRuleViolationError):
    def __init__(self, message: str = "Cart is empty"):
        super().__init__(message=message)
        self.code = "EMPTY_CART"


class InsufficientStockError(BusinessRuleViolationError):
    def __init__(self, message: str = "Insufficient stock"):
        super().__init__(message=message)
        self.code = "INSUFFICIENT_STOCK"


class SelfPurchaseError(BusinessRuleViolationError):
    def __init__(self, message: str = "Cannot purchase your own product"):
        super().__init__(message=message)
        self.code = "SELF_PURCHASE_NOT_ALLOWED"


class OrderCannotBeCancelledError(BusinessRuleViolationError):
    def __init__(self, message: str = "This order cannot be cancelled"):
        super().__init__(message=message)
        self.code = "ORDER_CANNOT_BE_CANCELLED"


class InvalidOrderStatusTransition(BusinessRuleViolationError):
    def __init__(self, from_status: str, to_status: str):
        message = f"Cannot transition order from '{from_status}' to '{to_status}'"
        super().__init__(message=message)
        self.code = "INVALID_STATUS_TRANSITION"


class SelfBanError(BusinessRuleViolationError):
    def __init__(self, message: str = "Cannot ban yourself"):
        super().__init__(message=message)
        self.code = "SELF_BAN_NOT_ALLOWED"


class UserAlreadyAdminError(BusinessRuleViolationError):
    def __init__(self, message: str = "User is already an admin or owner"):
        super().__init__(message=message)
        self.code = "USER_ALREADY_ADMIN"


class SelfDemoteError(BusinessRuleViolationError):
    def __init__(self, message: str = "Cannot demote yourself"):
        super().__init__(message=message)
        self.code = "SELF_DEMOTE_NOT_ALLOWED"


class ProductInUseError(ConflictError):
    def __init__(self, order_count: int):
        message = f"Cannot delete product: it is referenced in {order_count} order(s)"
        super().__init__(message=message)
        self.code = "PRODUCT_IN_USE"


# --- Validation Errors ---


class ValidationError(AppException):
    def __init__(self, message: str = "Validation error", details: Any = None):
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=422, details=details)


# --- File Upload Errors ---


class FileUploadError(AppException):
    def __init__(self, message: str = "File upload error"):
        super().__init__(message=message, code="FILE_UPLOAD_ERROR", status_code=400)


class FileTypeNotAllowedError(FileUploadError):
    def __init__(self, file_type: str, allowed_types: list[str]):
        message = f"File type '{file_type}' not allowed. Use: {', '.join(allowed_types)}"
        super().__init__(message=message)
        self.code = "FILE_TYPE_NOT_ALLOWED"


class FileTooLargeError(FileUploadError):
    def __init__(self, max_size_mb: int):
        message = f"File too large. Maximum size is {max_size_mb}MB"
        super().__init__(message=message)
        self.code = "FILE_TOO_LARGE"


# --- Infrastructure Errors ---


class InfrastructureError(AppException):
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message=message, code="INFRASTRUCTURE_ERROR", status_code=500)


class DatabaseError(InfrastructureError):
    def __init__(self, message: str = "Database error occurred"):
        super().__init__(message=message)
        self.code = "DATABASE_ERROR"


class ExternalServiceError(InfrastructureError):
    def __init__(self, service_name: str, message: str = "External service error"):
        super().__init__(message=f"{service_name}: {message}")
        self.code = "EXTERNAL_SERVICE_ERROR"
