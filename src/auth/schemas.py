from pydantic import BaseModel, model_validator
from datetime import datetime

class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    type: str  # "access" or "refresh"


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @model_validator(mode="after")
    def validate_passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")

        return self
