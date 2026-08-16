from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MachineBase(BaseModel):
    customer_id: str
    type: str = Field(min_length=2, max_length=80)
    brand: str | None = None
    model: str | None = None
    serial_number: str | None = None
    year: int | None = Field(default=None, ge=1900, le=2100)
    identification: str | None = None
    usage_hours: Decimal | None = Field(default=None, ge=0)
    notes: str | None = None
    is_active: bool = True


class MachineCreate(MachineBase):
    pass


class MachineUpdate(BaseModel):
    customer_id: str | None = None
    type: str | None = Field(default=None, min_length=2, max_length=80)
    brand: str | None = None
    model: str | None = None
    serial_number: str | None = None
    year: int | None = Field(default=None, ge=1900, le=2100)
    identification: str | None = None
    usage_hours: Decimal | None = Field(default=None, ge=0)
    notes: str | None = None
    is_active: bool | None = None


class MachineRead(MachineBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    customer_name: str | None = None
    created_at: datetime
    updated_at: datetime
