from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv

from app.core.config import settings


@dataclass(frozen=True)
class SicnetMigrationSettings:
    sqlserver_host: str
    sqlserver_database: str
    sqlserver_user: str | None
    sqlserver_password: str | None
    sqlserver_driver: str
    sqlserver_trusted_connection: bool
    destination_url: str

    @classmethod
    def from_env(cls) -> "SicnetMigrationSettings":
        load_dotenv("../.env", override=False)
        load_dotenv(".env", override=False)
        return cls(
            sqlserver_host=os.getenv("SICNET_DB_HOST", "localhost"),
            sqlserver_database=os.getenv("SICNET_DB_NAME", "SICNET_MIGRACAO"),
            sqlserver_user=_blank(os.getenv("SICNET_DB_USER")),
            sqlserver_password=_blank(os.getenv("SICNET_DB_PASSWORD")),
            sqlserver_driver=os.getenv("SICNET_DB_DRIVER", "ODBC Driver 18 for SQL Server"),
            sqlserver_trusted_connection=_truthy(os.getenv("SICNET_DB_TRUSTED_CONNECTION", "true")),
            destination_url=os.getenv("SUPABASE_DB_URL") or settings.SQLALCHEMY_DATABASE_URI,
        )


def _blank(value: str | None) -> str | None:
    value = (value or "").strip()
    return value or None


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "sim", "s", "y"}

