from datetime import datetime
from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    type: str  # "access" or "refresh"


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
