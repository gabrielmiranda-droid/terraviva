from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import BudgetItemType, BudgetStatus
from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Budget(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "budgets"

    number: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    work_order_id: Mapped[str] = mapped_column(ForeignKey("work_orders.id"), index=True, nullable=False)
    date: Mapped[date | None] = mapped_column(Date)
    valid_until: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    parts_subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    services_subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    status: Mapped[str] = mapped_column(
        String(40),
        default=BudgetStatus.RASCUNHO.value,
        index=True,
        nullable=False,
    )
    approval_method: Mapped[str | None] = mapped_column(String(80))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    responsible_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))

    work_order: Mapped["WorkOrder"] = relationship(back_populates="budgets")
    items: Mapped[list["BudgetItem"]] = relationship(back_populates="budget", cascade="all, delete-orphan")
    status_history: Mapped[list["BudgetStatusHistory"]] = relationship(
        back_populates="budget",
        cascade="all, delete-orphan",
    )


class BudgetItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "budget_items"

    budget_id: Mapped[str] = mapped_column(ForeignKey("budgets.id"), index=True, nullable=False)
    item_type: Mapped[str] = mapped_column(String(20), default=BudgetItemType.PECA.value, nullable=False)
    part_id: Mapped[str | None] = mapped_column(ForeignKey("parts.id"))
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    budget: Mapped["Budget"] = relationship(back_populates="items")
    part: Mapped["Part | None"] = relationship(back_populates="budget_items")


class BudgetStatusHistory(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "budget_status_history"

    budget_id: Mapped[str] = mapped_column(ForeignKey("budgets.id"), index=True, nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(40))
    to_status: Mapped[str] = mapped_column(String(40), nullable=False)
    changed_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)

    budget: Mapped["Budget"] = relationship(back_populates="status_history")
