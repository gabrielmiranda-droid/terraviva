import os
from decimal import Decimal

os.environ["AUTO_SEED"] = "false"
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.api.deps import get_db
from app.core.enums import FiscalInvoiceStatus, SaleStatus
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.seed import seed_roles
from app.main import app
from app.models.customer import Customer
from app.models.role import Role
from app.models.sale import Sale
from app.models.user import User
from app.services.sales import fiscal_snapshot_from_customer, fiscal_status_for_request


engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
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


def auth_headers() -> dict[str, str]:
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    login = client.post("/api/v1/auth/login", json={"email": "admin@geleia.local", "password": "admin123"})
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_fiscal_snapshot_uses_customer_data_without_second_customer_record() -> None:
    customer = Customer(
        name="Fazenda Santa Tereza",
        trade_name="Santa Tereza Agro LTDA",
        document="12345678000190",
        state_registration="9040000012",
        email="fiscal@santatereza.example",
        is_active=True,
    )

    assert fiscal_snapshot_from_customer(customer) == {
        "fiscal_document": "12345678000190",
        "fiscal_name": "Santa Tereza Agro LTDA",
        "fiscal_state_registration": "9040000012",
        "fiscal_email": "fiscal@santatereza.example",
    }
    assert fiscal_status_for_request(False) == FiscalInvoiceStatus.NOT_REQUESTED.value
    assert fiscal_status_for_request(True) == FiscalInvoiceStatus.PENDING.value


def test_sales_fiscal_invoice_filter_lists_pending_and_not_requested_sales() -> None:
    app.dependency_overrides[get_db] = override_get_db
    headers = auth_headers()
    db: Session = TestingSessionLocal()
    try:
        pending_sale = Sale(
            number="VEN-000001",
            status=SaleStatus.FINALIZADA.value,
            items_total=Decimal("100.00"),
            discount=Decimal("0.00"),
            total=Decimal("100.00"),
            fiscal_invoice_requested=True,
            fiscal_invoice_status=FiscalInvoiceStatus.PENDING.value,
            fiscal_document="12345678000190",
            fiscal_name="Fazenda Santa Tereza",
            fiscal_state_registration="9040000012",
            fiscal_email="fiscal@santatereza.example",
        )
        normal_sale = Sale(
            number="VEN-000002",
            status=SaleStatus.FINALIZADA.value,
            items_total=Decimal("89.90"),
            discount=Decimal("0.00"),
            total=Decimal("89.90"),
            fiscal_invoice_requested=False,
            fiscal_invoice_status=FiscalInvoiceStatus.NOT_REQUESTED.value,
        )
        db.add_all([pending_sale, normal_sale])
        db.commit()
    finally:
        db.close()

    client = TestClient(app)
    pending = client.get("/api/v1/sales", params={"fiscal_invoice": "pending"}, headers=headers)
    assert pending.status_code == 200
    assert [sale["number"] for sale in pending.json()] == ["VEN-000001"]
    assert pending.json()[0]["fiscal_invoice_status"] == "PENDING"

    not_requested = client.get("/api/v1/sales", params={"fiscal_invoice": "not_requested"}, headers=headers)
    assert not_requested.status_code == 200
    assert [sale["number"] for sale in not_requested.json()] == ["VEN-000002"]
    assert not_requested.json()[0]["fiscal_invoice_status"] == "NOT_REQUESTED"

