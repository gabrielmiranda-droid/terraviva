from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import WorkOrderStatus
from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class WorkOrder(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "work_orders"

    number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    entry_id: Mapped[str] = mapped_column(ForeignKey("machine_entries.id"), unique=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), index=True, nullable=False)
    machine_id: Mapped[str] = mapped_column(ForeignKey("machines.id"), index=True, nullable=False)
    technician_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    reported_problem: Mapped[str] = mapped_column(Text, nullable=False)
    diagnosis: Mapped[str | None] = mapped_column(Text)
    internal_notes: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(20), default="NORMAL", nullable=False)
    status: Mapped[str] = mapped_column(
        String(40),
        default=WorkOrderStatus.RECEBIDA.value,
        index=True,
        nullable=False,
    )
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    parts_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    services_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    entry: Mapped["MachineEntry"] = relationship(back_populates="work_order")
    customer: Mapped["Customer"] = relationship(back_populates="work_orders")
    machine: Mapped["Machine"] = relationship(back_populates="work_orders")
    technician: Mapped["User | None"] = relationship(
        back_populates="assigned_work_orders",
        foreign_keys=[technician_id],
    )
    status_history: Mapped[list["WorkOrderStatusHistory"]] = relationship(
        back_populates="work_order",
        cascade="all, delete-orphan",
    )
    budgets: Mapped[list["Budget"]] = relationship(back_populates="work_order")


class WorkOrderStatusHistory(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "work_order_status_history"

    work_order_id: Mapped[str] = mapped_column(ForeignKey("work_orders.id"), index=True, nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(40))
    to_status: Mapped[str] = mapped_column(String(40), nullable=False)
    changed_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)

    work_order: Mapped["WorkOrder"] = relationship(back_populates="status_history")
