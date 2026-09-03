from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, gt=0)
    LOGIN_RATE_LIMIT: int = Field(default=10, gt=0)
    LOGIN_RATE_WINDOW_SECONDS: int = Field(default=60, gt=0)

    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parents[2] / '.env', extra='ignore')

settings = Settings()
