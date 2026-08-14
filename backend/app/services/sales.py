from sqlalchemy.orm import Session

from app.core.enums import FiscalInvoiceStatus
from app.models.customer import Customer
from app.models.sale import Sale


def fiscal_snapshot_from_customer(customer: Customer | None) -> dict[str, str | None]:
    if not customer:
        return {
            "fiscal_document": None,
            "fiscal_name": None,
            "fiscal_state_registration": None,
            "fiscal_email": None,
        }
    return {
        "fiscal_document": customer.document,
        "fiscal_name": customer.trade_name or customer.name,
        "fiscal_state_registration": customer.state_registration,
        "fiscal_email": customer.email,
    }


def fiscal_status_for_request(requested: bool) -> str:
    return FiscalInvoiceStatus.PENDING.value if requested else FiscalInvoiceStatus.NOT_REQUESTED.value


def list_sales(
    db: Session,
    *,
    fiscal_invoice: str | None,
    offset: int,
    limit: int,
) -> list[Sale]:
    query = db.query(Sale)
    if fiscal_invoice == "pending":
        query = query.filter(Sale.fiscal_invoice_status == FiscalInvoiceStatus.PENDING.value)
    elif fiscal_invoice == "not_requested":
        query = query.filter(Sale.fiscal_invoice_status == FiscalInvoiceStatus.NOT_REQUESTED.value)
    return query.order_by(Sale.created_at.desc()).offset(offset).limit(limit).all()

