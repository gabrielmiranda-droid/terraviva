from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerBase(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    trade_name: str | None = None
    document: str | None = None
    state_registration: str | None = None
    phone: str | None = None
    whatsapp: str | None = None
    email: EmailStr | None = None
    zip_code: str | None = None
    address: str | None = None
    number: str | None = None
    complement: str | None = None
    district: str | None = None
    city: str | None = None
    state: str | None = Field(default=None, max_length=2)
    notes: str | None = None
    is_active: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    trade_name: str | None = None
    document: str | None = None
    state_registration: str | None = None
    phone: str | None = None
    whatsapp: str | None = None
    email: EmailStr | None = None
    zip_code: str | None = None
    address: str | None = None
    number: str | None = None
    complement: str | None = None
    district: str | None = None
    city: str | None = None
    state: str | None = Field(default=None, max_length=2)
    notes: str | None = None
    is_active: bool | None = None


class CustomerRead(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
