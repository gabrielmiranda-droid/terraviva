import os
import secrets
import sys
from pathlib import Path

from sqlalchemy import inspect, text
import uvicorn

db_path = Path(__file__).resolve().parents[1] / "dev_local.db"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DATABASE_URL", f"sqlite+pysqlite:///{db_path.as_posix()}")
os.environ.setdefault("AUTO_SEED", "true")
os.environ.setdefault("LEGACY_SIC_XLSX_PATH", "../data/GELEIA.xlsx")

from app import models  # noqa: E402,F401
from app.core.config import settings  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.seed import seed_initial_data  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.machine_entry import MachineEntry  # noqa: E402


def sync_dev_admin_password() -> None:
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == settings.FIRST_SUPERUSER_EMAIL).first()
        if admin:
            admin.hashed_password = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)
            db.commit()
    finally:
        db.close()


def ensure_dev_schema() -> None:
    inspector = inspect(engine)
    if "machine_entries" not in inspector.get_table_names():
        return
    existing_columns = {column["name"] for column in inspector.get_columns("machine_entries")}
    columns = {
        "public_token": "ALTER TABLE machine_entries ADD COLUMN public_token VARCHAR(64)",
        "delivered_at": "ALTER TABLE machine_entries ADD COLUMN delivered_at DATETIME",
        "delivered_by_user_id": "ALTER TABLE machine_entries ADD COLUMN delivered_by_user_id VARCHAR(36)",
        "receiver_name": "ALTER TABLE machine_entries ADD COLUMN receiver_name VARCHAR(180)",
        "delivery_notes": "ALTER TABLE machine_entries ADD COLUMN delivery_notes TEXT",
    }
    with engine.begin() as connection:
        for name, statement in columns.items():
            if name not in existing_columns:
                connection.execute(text(statement))

    db = SessionLocal()
    try:
        for entry in db.query(MachineEntry).filter(MachineEntry.public_token.is_(None)).all():
            entry.public_token = secrets.token_urlsafe(24)
        db.commit()
    finally:
        db.close()


def main() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_dev_schema()
    seed_initial_data()
    sync_dev_admin_password()
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
