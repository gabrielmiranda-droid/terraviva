from __future__ import annotations

from sqlalchemy import JSON, Boolean, Text, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Customer(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "customers"
    __table_args__ = (UniqueConstraint("legacy_source", "legacy_sic_id", name="uq_customers_legacy_sic"),)

    legacy_source: Mapped[str | None] = mapped_column(String(40))
    legacy_sic_id: Mapped[str | None] = mapped_column(String(80))
    legacy_code: Mapped[str | None] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    trade_name: Mapped[str | None] = mapped_column(String(180))
    document: Mapped[str | None] = mapped_column(String(32), index=True)
    state_registration: Mapped[str | None] = mapped_column(String(40))
    phone: Mapped[str | None] = mapped_column(String(40))
    whatsapp: Mapped[str | None] = mapped_column(String(40))
    email: Mapped[str | None] = mapped_column(String(255))
    zip_code: Mapped[str | None] = mapped_column(String(16))
    address: Mapped[str | None] = mapped_column(String(255))
    number: Mapped[str | None] = mapped_column(String(30))
    complement: Mapped[str | None] = mapped_column(String(120))
    district: Mapped[str | None] = mapped_column(String(120))
    city: Mapped[str | None] = mapped_column(String(120))
    state: Mapped[str | None] = mapped_column(String(2))
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    legacy_payload: Mapped[dict | None] = mapped_column(JSON)

    machines: Mapped[list["Machine"]] = relationship(back_populates="customer")
    machine_entries: Mapped[list["MachineEntry"]] = relationship(back_populates="customer")
    work_orders: Mapped[list["WorkOrder"]] = relationship(back_populates="customer")
    sales: Mapped[list["Sale"]] = relationship(back_populates="customer")
