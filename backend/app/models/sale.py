from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import SaleStatus
from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Sale(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "sales"

    number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    customer_id: Mapped[str | None] = mapped_column(ForeignKey("customers.id"), index=True)
    seller_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(
        String(30),
        default=SaleStatus.ABERTA.value,
        index=True,
        nullable=False,
    )
    sold_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    items_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)

    customer: Mapped["Customer | None"] = relationship(back_populates="sales")
    items: Mapped[list["SaleItem"]] = relationship(back_populates="sale", cascade="all, delete-orphan")
    payments: Mapped[list["Payment"]] = relationship(back_populates="sale")


class SaleItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "sale_items"

    sale_id: Mapped[str] = mapped_column(ForeignKey("sales.id"), index=True, nullable=False)
    part_id: Mapped[str] = mapped_column(ForeignKey("parts.id"), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    sale: Mapped["Sale"] = relationship(back_populates="items")
    part: Mapped["Part"] = relationship(back_populates="sale_items")
