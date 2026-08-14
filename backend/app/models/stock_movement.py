from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import UUIDPrimaryKeyMixin


class StockMovement(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "stock_movements"

    part_id: Mapped[str] = mapped_column(ForeignKey("parts.id"), index=True, nullable=False)
    movement_type: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    previous_stock: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    resulting_stock: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    unit_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    reference_entity: Mapped[str | None] = mapped_column(String(80))
    reference_id: Mapped[str | None] = mapped_column(String(36), index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    legacy_source: Mapped[str | None] = mapped_column(String(40))
    legacy_sic_id: Mapped[str | None] = mapped_column(String(80))
    created_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    part: Mapped["Part"] = relationship(back_populates="stock_movements")
