from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.core.enums import PrintDocumentType
from app.schemas.customer import CustomerRead
from app.schemas.machine import MachineRead
from app.schemas.machine_entry import MachineEntryRead
from app.schemas.work_order import WorkOrderRead, WorkOrderStatusHistoryRead


class WorkshopMachineRead(BaseModel):
    entry_id: str
    entry_number: str
    entry_public_token: str
    work_order_id: str
    work_order_number: str
    customer_id: str
    customer_name: str
    customer_phone: str | None
    machine_id: str
    machine_type: str
    machine_brand: str | None
    machine_model: str | None
    machine_serial_number: str | None
    entered_at: datetime
    days_in_shop: int
    attendance_type: str
    status: str
    technician_id: str | None
    technician_name: str | None
    reported_problem: str


class WorkOrderDetailRead(BaseModel):
    work_order: WorkOrderRead
    entry: MachineEntryRead
    customer: CustomerRead
    machine: MachineRead
    history: list[WorkOrderStatusHistoryRead]


class WorkOrderStatusUpdate(BaseModel):
    status: str
    reason: str | None = None
    diagnosis: str | None = None
    internal_notes: str | None = None


class PrintJobCreate(BaseModel):
    document_type: PrintDocumentType
    printer_name: str | None = None


class PrintJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_type: str
    reference_type: str
    reference_id: str
    status: str
    printer_name: str | None
    printed_at: datetime | None
    printed_by_user_id: str | None
    created_at: datetime
    updated_at: datetime


class ProductStockHealth(BaseModel):
    total_products: int
    negative_stock: int
    zero_price: int
    estimated_stock_value: Decimal
