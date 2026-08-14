from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import AttendanceType


class MachineEntryCreate(BaseModel):
    customer_id: str
    machine_id: str
    reported_problem: str = Field(min_length=3)
    attendance_type: AttendanceType
    notes: str | None = None
    accessories: str | None = None
    visual_condition: str | None = None


class MachineEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    number: str
    public_token: str
    customer_id: str
    machine_id: str
    entry_date: datetime
    reported_problem: str
    attendance_type: str
    notes: str | None
    received_by_user_id: str | None
    accessories: str | None
    visual_condition: str | None
    status: str
    delivered_at: datetime | None
    delivered_by_user_id: str | None
    receiver_name: str | None
    delivery_notes: str | None
    created_at: datetime
    updated_at: datetime


class MachineEntryWithWorkOrder(BaseModel):
    entry: MachineEntryRead
    work_order_id: str
    work_order_number: str


class MachineEntryDeliveryCreate(BaseModel):
    receiver_name: str | None = None
    delivery_notes: str | None = None
