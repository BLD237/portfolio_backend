from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Mufor Belmond Piannow Portfolio API"
    api_prefix: str = "/api"
    database_url: str = f"sqlite:///{Path(__file__).resolve().parents[2] / 'portfolio.db'}"
    secret_key: str = "change-this-secret-in-production"
    access_token_expire_minutes: int = 60 * 24
    admin_email: str = "admin@belmond.dev"
    admin_password: str = "ChangeMe123!"
    cors_origins: str = "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001"

    # Contact notification config
    contact_recipient_email: str = "muforbelmond20@gmail.com,muforbelmond@icloud.com"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "muforbelmond20@gmail.com"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
