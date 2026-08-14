from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PartBase(BaseModel):
    legacy_code: str | None = None
    internal_code: str | None = None
    barcode: str | None = None
    description: str = Field(min_length=2, max_length=255)
    brand: str | None = None
    manufacturer: str | None = None
    supplier_id: str | None = None
    location: str | None = None
    unit: str = "UN"
    cost_price: Decimal = Field(default=Decimal("0"), ge=0)
    sale_price: Decimal = Field(default=Decimal("0"), ge=0)
    current_stock: Decimal = Field(default=Decimal("0"), ge=0)
    minimum_stock: Decimal = Field(default=Decimal("0"), ge=0)
    notes: str | None = None


class PartCreate(PartBase):
    pass


class PartRead(PartBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PartSearchRead(BaseModel):
    id: str
    code: str | None
    internal_code: str | None
    barcode: str | None
    description: str
    manufacturer: str | None
    stock_available: Decimal
    sale_price: Decimal
    location: str | None
    unit: str
