from fastapi import HTTPException, status
from src.users.models import User
from src.users.role import UserRole


def require_admin(user: User) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user
