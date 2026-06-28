from pydantic import BaseModel
from src.users.role import UserRole


class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}


class UserUpdateRole(BaseModel):
    role: UserRole


class UserBan(BaseModel):
    is_active: bool
