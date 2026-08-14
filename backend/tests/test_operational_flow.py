import os
from collections.abc import Generator

os.environ["AUTO_SEED"] = "false"
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.seed import seed_roles
from app.main import app
from app.models.role import Role
from app.models.user import User
from app import models  # noqa: F401


engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def setup_module() -> None:
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        seed_roles(db)
        admin_role = db.query(Role).filter(Role.name == "ADMIN").one()
        db.add(
            User(
                email="admin@geleia.local",
                full_name="Administrador",
                hashed_password=get_password_hash("admin123"),
                role=admin_role,
                is_active=True,
            )
        )
        db.commit()
    finally:
        db.close()


def teardown_module() -> None:
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_customer_machine_entry_creates_work_order() -> None:
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    login = client.post("/api/v1/auth/login", json={"email": "admin@geleia.local", "password": "admin123"})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    customer = client.post(
        "/api/v1/customers",
        json={"name": "Cliente Teste", "whatsapp": "44999990000"},
        headers=headers,
    )
    assert customer.status_code == 201
    customer_id = customer.json()["id"]

    machine = client.post(
        "/api/v1/machines",
        json={
            "customer_id": customer_id,
            "type": "Trator",
            "brand": "Teste",
            "model": "T100",
            "identification": "Fazenda 1",
        },
        headers=headers,
    )
    assert machine.status_code == 201
    machine_id = machine.json()["id"]

    entry = client.post(
        "/api/v1/machine-entries",
        json={
            "customer_id": customer_id,
            "machine_id": machine_id,
            "attendance_type": "ORCAMENTO",
            "reported_problem": "Nao liga pela manha",
        },
        headers=headers,
    )
    assert entry.status_code == 201
    assert entry.json()["work_order_number"] == "OS-000001"

    work_orders = client.get("/api/v1/work-orders", headers=headers)
    assert work_orders.status_code == 200
    assert work_orders.json()[0]["status"] == "AGUARDANDO_DIAGNOSTICO"

    in_shop = client.get("/api/v1/machine-entries/in-shop", headers=headers)
    assert in_shop.status_code == 200
    assert in_shop.json()[0]["entry_number"] == "ENT-000001"

    delivered = client.post(f"/api/v1/machine-entries/{entry.json()['entry']['id']}/deliver", json={}, headers=headers)
    assert delivered.status_code == 200
    assert delivered.json()["delivered_at"] is not None

    in_shop_after_delivery = client.get("/api/v1/machine-entries/in-shop", headers=headers)
    assert in_shop_after_delivery.status_code == 200
    assert in_shop_after_delivery.json() == []
