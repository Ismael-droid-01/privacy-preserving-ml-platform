from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    ALLOWED_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()