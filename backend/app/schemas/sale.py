from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr

from app.core.enums import FiscalInvoiceStatus


class FiscalInvoiceSnapshot(BaseModel):
    fiscal_invoice_requested: bool = False
    fiscal_invoice_status: FiscalInvoiceStatus = FiscalInvoiceStatus.NOT_REQUESTED
    fiscal_document: str | None = None
    fiscal_name: str | None = None
    fiscal_state_registration: str | None = None
    fiscal_email: EmailStr | None = None


class SaleRead(FiscalInvoiceSnapshot):
    model_config = ConfigDict(from_attributes=True)

    id: str
    number: str
    customer_id: str | None
    seller_id: str | None
    status: str
    sold_at: datetime | None
    items_total: Decimal
    discount: Decimal
    total: Decimal
    created_at: datetime
    updated_at: datetime

