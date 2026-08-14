from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import PaymentStatus
from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Payment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "payments"

    sale_id: Mapped[str | None] = mapped_column(ForeignKey("sales.id"), index=True)
    work_order_id: Mapped[str | None] = mapped_column(ForeignKey("work_orders.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    method: Mapped[str] = mapped_column(String(60), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30),
        default=PaymentStatus.PENDENTE.value,
        index=True,
        nullable=False,
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)

    sale: Mapped["Sale | None"] = relationship(back_populates="payments")
