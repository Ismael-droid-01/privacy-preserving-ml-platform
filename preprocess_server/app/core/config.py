from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    UPLOAD_DIR: str = "temp"
    RAW_DATA_PATH: str = "temp/raw"
    PROCESSED_DATA_PATH: str = "temp/processed"
  
    ALLOWED_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()