from functools import lru_cache

from pydantic import Field, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ERP Oficina Agricola"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "erp_user"
    POSTGRES_PASSWORD: str = "erp_password"
    POSTGRES_DB: str = "erp_oficina"
    DATABASE_URL: str | None = None

    SECRET_KEY: str = Field(default="change-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    FIRST_SUPERUSER_EMAIL: str = "admin@geleia.local"
    FIRST_SUPERUSER_PASSWORD: str = "123456"
    FIRST_SUPERUSER_NAME: str = "Administrador"
    AUTO_SEED: bool = True

    LEGACY_SIC_XLSX_PATH: str = "../data/GELEIA.xlsx"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            placeholders = ("SEU_PROJECT_REF", "SUA_SENHA", "COLOQUE-SUA-SENHA-AQUI")
            if any(placeholder in self.DATABASE_URL for placeholder in placeholders):
                raise ValueError(
                    "DATABASE_URL ainda esta com placeholder. Preencha a connection string real do Supabase no .env."
                )
            return self.DATABASE_URL
        return str(
            PostgresDsn.build(
                scheme="postgresql+psycopg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
