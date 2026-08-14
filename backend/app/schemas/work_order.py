from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class WorkOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    number: str
    entry_id: str
    customer_id: str
    machine_id: str
    technician_id: str | None
    reported_problem: str
    diagnosis: str | None
    internal_notes: str | None
    priority: str
    status: str
    opened_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    delivered_at: datetime | None
    parts_total: Decimal
    services_total: Decimal
    discount: Decimal
    total: Decimal
    created_at: datetime
    updated_at: datetime


class WorkOrderStatusHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    work_order_id: str
    from_status: str | None
    to_status: str
    changed_by_user_id: str | None
    changed_at: datetime
    reason: str | None
