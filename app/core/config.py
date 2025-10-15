# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 🔹 Gemini API
    GEMINI_API_KEY: str

    # 🔹 Database 설정
    DB_KIND: str = "postgres"
    DB_HOST: str = "49.50.134.193"
    DB_PORT: int = 5432
    DB_USER: str = "admin"
    DB_PASSWORD: str = "1234"
    DB_NAME: str = "gongcaedan"

    # 🔹 pydantic-settings v2 구성
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,  # .env에서 대소문자 섞여도 인식
    )

settings = Settings()
