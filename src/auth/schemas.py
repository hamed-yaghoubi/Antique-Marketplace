from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime

class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    type: str  # "access" or "refresh"


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("username")
    @classmethod
    def strip_username(cls, v: str) -> str:
        return v.strip()


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def validate_passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")

        # Check password complexity
        if not any(c.isupper() for c in self.new_password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in self.new_password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in self.new_password):
            raise ValueError("Password must contain at least one digit")

        return self
