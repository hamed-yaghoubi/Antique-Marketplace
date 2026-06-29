from enum import StrEnum


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"
    OWNER = "owner"
