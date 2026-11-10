from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "DarMate API"
    environment: str = "development"

    database_url: str | None = None  # surcharge (tests) ; sinon MySQL ci-dessous
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "darmate_user"
    db_password: str = ""
    db_name: str = "darmate"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    password_reset_expire_minutes: int = 30
    max_failed_logins: int = 5
    lockout_minutes: int = 15

    cookie_secure: bool = False  # True en production (HTTPS)
    cookie_samesite: str = "strict"
    rate_limit_enabled: bool = True

    cors_origins: list[str] = ["http://localhost:4200"]
    frontend_url: str = "http://localhost:4200"

    upload_dir: str = "uploads"
    max_image_mb: int = 5
    max_document_mb: int = 10

    admin_email: str = "admin@darmate.local"
    admin_password: str = ""

    @property
    def sqlalchemy_url(self) -> str:
        if self.database_url:
            return self.database_url
        return URL.create(
            "mysql+pymysql", username=self.db_user, password=self.db_password,
            host=self.db_host, port=self.db_port, database=self.db_name,
            query={"charset": "utf8mb4"},
        ).render_as_string(hide_password=False)

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
