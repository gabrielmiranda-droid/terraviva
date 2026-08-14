from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.operations import WorkOrderDetailRead, WorkOrderStatusUpdate
from app.schemas.work_order import WorkOrderRead
from app.services.work_orders import (
    get_work_order_detail_or_404,
    get_work_order_or_404,
    list_work_orders,
    update_work_order_status,
)

router = APIRouter()


@router.get("", response_model=list[WorkOrderRead])
def list_(
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
    offset: int = 0,
    limit: int = Query(default=100, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_work_orders(db, status_filter=status, search=search, offset=offset, limit=limit)


@router.get("/{work_order_id}", response_model=WorkOrderRead)
def get(
    work_order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_work_order_or_404(db, work_order_id)


@router.get("/{work_order_id}/detail", response_model=WorkOrderDetailRead)
def detail(
    work_order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    work_order = get_work_order_detail_or_404(db, work_order_id)
    return {
        "work_order": work_order,
        "entry": work_order.entry,
        "customer": work_order.customer,
        "machine": work_order.machine,
        "history": sorted(work_order.status_history, key=lambda item: item.changed_at),
    }


@router.patch("/{work_order_id}/status", response_model=WorkOrderRead)
def update_status(
    work_order_id: str,
    payload: WorkOrderStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_work_order_status(
        db,
        work_order_id=work_order_id,
        payload=payload,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )
