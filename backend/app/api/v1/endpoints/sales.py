from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.sale import SaleRead
from app.services.sales import list_sales

router = APIRouter()


@router.get("", response_model=list[SaleRead])
def list_(
    fiscal_invoice: str | None = Query(default=None, pattern="^(pending|not_requested)$"),
    offset: int = 0,
    limit: int = Query(default=100, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_sales(db, fiscal_invoice=fiscal_invoice, offset=offset, limit=limit)
