from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    UPLOAD_DIR: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_TOKEN_COOKIE_NAME: str = "refresh_token"
    COOKIE_PATH: str = "/auth"
    COOKIE_MAX_AGE: int = 604800
    COOKIE_SECURE: bool = True
    COOKIE_SAMESITE: str = "strict"
    CORS_ORIGINS: str = "http://localhost:3000"
    ALLOWED_IMAGE_EXTENSIONS: str = ".jpg,.jpeg,.png,.gif,.webp"
    MAX_IMAGE_SIZE: int = 5242880

    @property
    def allowed_image_extensions_set(self) -> set[str]:
        return {ext.strip() for ext in self.ALLOWED_IMAGE_EXTENSIONS.split(",")}

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()