from pydantic import BaseModel, model_validator
from src.core.schemas import TokenResponse


Token = TokenResponse


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
