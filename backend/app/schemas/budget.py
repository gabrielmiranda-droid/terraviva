from __future__ import annotations

from datetime import date as date_type
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BudgetItemUpsert(BaseModel):
    id: str | None = None
    item_type: str
    part_id: str | None = None
    description: str = Field(min_length=2, max_length=255)
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    discount: Decimal = Field(default=Decimal("0"), ge=0)


class BudgetUpdate(BaseModel):
    date: date_type | None = None
    valid_until: date_type | None = None
    notes: str | None = None
    discount: Decimal = Field(default=Decimal("0"), ge=0)
    items: list[BudgetItemUpsert] = []


class BudgetDecisionCreate(BaseModel):
    method: str | None = None
    reason: str | None = None
    note: str | None = None


class BudgetItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    budget_id: str
    item_type: str
    part_id: str | None
    description: str
    quantity: Decimal
    unit_price: Decimal
    discount: Decimal
    total: Decimal


class BudgetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    number: str
    version: int
    work_order_id: str
    date: date_type | None
    valid_until: date_type | None
    notes: str | None
    parts_subtotal: Decimal
    services_subtotal: Decimal
    discount: Decimal
    total: Decimal
    status: str
    approval_method: str | None
    approved_at: datetime | None
    rejected_at: datetime | None
    rejection_reason: str | None
    responsible_user_id: str | None
    items: list[BudgetItemRead] = []
    created_at: datetime
    updated_at: datetime
