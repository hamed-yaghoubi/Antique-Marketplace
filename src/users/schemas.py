from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import datetime
from src.users.role import UserRole

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(min_length=8)
    confirm_password: str

    @model_validator(mode="after")
    def validate_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")

        # Check password complexity
        if not any(c.isupper() for c in self.password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in self.password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in self.password):
            raise ValueError("Password must contain at least one digit")

        return self

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: str | None = None
