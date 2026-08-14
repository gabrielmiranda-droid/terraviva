from __future__ import annotations

from decimal import Decimal

from sqlalchemy import JSON, Boolean, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class PartCategory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "part_categories"

    name: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    parts: Mapped[list["Part"]] = relationship(back_populates="category")


class Supplier(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "suppliers"
    __table_args__ = (UniqueConstraint("legacy_source", "legacy_sic_id", name="uq_suppliers_legacy_sic"),)

    legacy_source: Mapped[str | None] = mapped_column(String(40))
    legacy_sic_id: Mapped[str | None] = mapped_column(String(80))
    legacy_code: Mapped[str | None] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(180))
    document: Mapped[str | None] = mapped_column(String(32), index=True)
    state_registration: Mapped[str | None] = mapped_column(String(40))
    phone: Mapped[str | None] = mapped_column(String(40))
    email: Mapped[str | None] = mapped_column(String(255))
    zip_code: Mapped[str | None] = mapped_column(String(16))
    address: Mapped[str | None] = mapped_column(String(255))
    district: Mapped[str | None] = mapped_column(String(120))
    city: Mapped[str | None] = mapped_column(String(120))
    state: Mapped[str | None] = mapped_column(String(2))
    bank_reference: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    legacy_payload: Mapped[dict | None] = mapped_column(JSON)

    parts: Mapped[list["Part"]] = relationship(back_populates="supplier")


class ProductLocation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "product_locations"
    __table_args__ = (UniqueConstraint("legacy_source", "legacy_sic_id", name="uq_product_locations_legacy_sic"),)

    name: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    legacy_source: Mapped[str | None] = mapped_column(String(40))
    legacy_sic_id: Mapped[str | None] = mapped_column(String(80))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    legacy_payload: Mapped[dict | None] = mapped_column(JSON)

    parts: Mapped[list["Part"]] = relationship(back_populates="product_location")


class Part(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "parts"
    __table_args__ = (UniqueConstraint("legacy_source", "legacy_sic_id", name="uq_parts_legacy_sic"),)

    legacy_source: Mapped[str | None] = mapped_column(String(40))
    legacy_sic_id: Mapped[str | None] = mapped_column(String(80))
    legacy_code: Mapped[str | None] = mapped_column(String(80), index=True)
    internal_code: Mapped[str | None] = mapped_column(String(80), unique=True, index=True)
    barcode: Mapped[str | None] = mapped_column(String(80), index=True)
    description: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    category_id: Mapped[str | None] = mapped_column(ForeignKey("part_categories.id"))
    brand: Mapped[str | None] = mapped_column(String(120))
    manufacturer: Mapped[str | None] = mapped_column(String(180))
    unit: Mapped[str] = mapped_column(String(12), default="UN", nullable=False)
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    average_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    sale_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    current_stock: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0, nullable=False)
    minimum_stock: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0, nullable=False)
    location: Mapped[str | None] = mapped_column(String(120))
    location_id: Mapped[str | None] = mapped_column(ForeignKey("product_locations.id"))
    supplier_id: Mapped[str | None] = mapped_column(ForeignKey("suppliers.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    import_origin: Mapped[str | None] = mapped_column(String(80))
    tributary_barcode: Mapped[str | None] = mapped_column(String(80))
    fiscal_data: Mapped[dict | None] = mapped_column(JSON)
    legacy_payload: Mapped[dict | None] = mapped_column(JSON)
    needs_inventory_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    inventory_review_reasons: Mapped[list[str] | None] = mapped_column(JSON)

    category: Mapped["PartCategory | None"] = relationship(back_populates="parts")
    supplier: Mapped["Supplier | None"] = relationship(back_populates="parts")
    product_location: Mapped["ProductLocation | None"] = relationship(back_populates="parts")
    budget_items: Mapped[list["BudgetItem"]] = relationship(back_populates="part")
    stock_movements: Mapped[list["StockMovement"]] = relationship(back_populates="part")
    sale_items: Mapped[list["SaleItem"]] = relationship(back_populates="part")
