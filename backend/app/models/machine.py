from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Machine(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "machines"

    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), index=True, nullable=False)
    type: Mapped[str] = mapped_column(String(80), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(120))
    model: Mapped[str | None] = mapped_column(String(120))
    serial_number: Mapped[str | None] = mapped_column(String(120), index=True)
    year: Mapped[int | None]
    identification: Mapped[str | None] = mapped_column(String(160), index=True)
    usage_hours: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    customer: Mapped["Customer"] = relationship(back_populates="machines")
    entries: Mapped[list["MachineEntry"]] = relationship(back_populates="machine")
    work_orders: Mapped[list["WorkOrder"]] = relationship(back_populates="machine")
