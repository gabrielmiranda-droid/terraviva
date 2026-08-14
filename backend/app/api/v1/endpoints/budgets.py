from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.budget import BudgetDecisionCreate, BudgetRead, BudgetUpdate
from app.schemas.operations import WorkshopMachineRead
from app.services.budgets import (
    approve_budget,
    create_or_get_budget,
    finalize_budget,
    get_active_budget_for_work_order,
    list_pending_budgets,
    reject_budget,
    update_budget,
)

router = APIRouter()


@router.get("/pending", response_model=list[WorkshopMachineRead])
def pending(
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    offset: int = 0,
    limit: int = Query(default=100, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_pending_budgets(db, status_filter=status, search=search, offset=offset, limit=limit)


@router.get("/work-orders/{work_order_id}/budget", response_model=BudgetRead | None)
def get_for_work_order(
    work_order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_active_budget_for_work_order(db, work_order_id)


@router.post("/work-orders/{work_order_id}/budget", response_model=BudgetRead, status_code=201)
def create_for_work_order(
    work_order_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_or_get_budget(
        db,
        work_order_id=work_order_id,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )


@router.put("/{budget_id}", response_model=BudgetRead)
def update(
    budget_id: str,
    payload: BudgetUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_budget(
        db,
        budget_id=budget_id,
        payload=payload,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )


@router.post("/{budget_id}/finalize", response_model=BudgetRead)
def finalize(
    budget_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return finalize_budget(
        db,
        budget_id=budget_id,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )


@router.post("/{budget_id}/approve", response_model=BudgetRead)
def approve(
    budget_id: str,
    payload: BudgetDecisionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return approve_budget(
        db,
        budget_id=budget_id,
        payload=payload,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )


@router.post("/{budget_id}/reject", response_model=BudgetRead)
def reject(
    budget_id: str,
    payload: BudgetDecisionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return reject_budget(
        db,
        budget_id=budget_id,
        payload=payload,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )
