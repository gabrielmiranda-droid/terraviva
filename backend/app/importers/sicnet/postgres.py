from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from app.importers.sicnet.config import SicnetMigrationSettings


def create_destination_engine(settings: SicnetMigrationSettings) -> Engine:
    connect_args = {"connect_timeout": 10} if settings.destination_url.startswith("postgres") else {}
    return create_engine(settings.destination_url, connect_args=connect_args, pool_pre_ping=True, future=True)

