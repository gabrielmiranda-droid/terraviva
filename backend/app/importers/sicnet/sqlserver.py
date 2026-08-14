from __future__ import annotations

from collections.abc import Iterable
from contextlib import contextmanager
from typing import Any

from app.importers.sicnet.config import SicnetMigrationSettings


class SqlServerConnectionError(RuntimeError):
    pass


def _pyodbc():
    try:
        import pyodbc  # type: ignore
    except ModuleNotFoundError as exc:
        raise SqlServerConnectionError(
            "pyodbc nao esta instalado. Rode: python -m pip install -r requirements.txt"
        ) from exc
    return pyodbc


def connection_string(settings: SicnetMigrationSettings) -> str:
    parts = [
        f"DRIVER={{{settings.sqlserver_driver}}}",
        f"SERVER={settings.sqlserver_host}",
        f"DATABASE={settings.sqlserver_database}",
        "Encrypt=no",
        "TrustServerCertificate=yes",
        "ApplicationIntent=ReadOnly",
    ]
    if settings.sqlserver_trusted_connection:
        parts.append("Trusted_Connection=yes")
    else:
        if not settings.sqlserver_user or not settings.sqlserver_password:
            raise SqlServerConnectionError(
                "Configure SICNET_DB_USER/SICNET_DB_PASSWORD ou use SICNET_DB_TRUSTED_CONNECTION=true."
            )
        parts += [f"UID={settings.sqlserver_user}", f"PWD={settings.sqlserver_password}"]
    return ";".join(parts)


@contextmanager
def connect(settings: SicnetMigrationSettings):
    pyodbc = _pyodbc()
    connection = pyodbc.connect(connection_string(settings), autocommit=True, timeout=15)
    try:
        yield connection
    finally:
        connection.close()


def fetch_all(connection: Any, sql: str, params: Iterable[Any] | None = None) -> list[dict[str, Any]]:
    cursor = connection.cursor()
    cursor.execute(sql, tuple(params or ()))
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def fetch_one(connection: Any, sql: str, params: Iterable[Any] | None = None) -> dict[str, Any] | None:
    rows = fetch_all(connection, sql, params)
    return rows[0] if rows else None

