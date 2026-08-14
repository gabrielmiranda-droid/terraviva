from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.machine import MachineCreate, MachineRead, MachineUpdate
from app.services.machines import create_machine, get_machine_or_404, list_machines, update_machine

router = APIRouter()


@router.get("", response_model=list[MachineRead])
def list_(
    search: str | None = Query(default=None),
    customer_id: str | None = Query(default=None),
    offset: int = 0,
    limit: int = Query(default=100, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_machines(db, query=search, customer_id=customer_id, offset=offset, limit=limit)


@router.post("", response_model=MachineRead, status_code=201)
def create(
    payload: MachineCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_machine(
        db,
        payload=payload,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )


@router.get("/{machine_id}", response_model=MachineRead)
def get(machine_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_machine_or_404(db, machine_id)


@router.patch("/{machine_id}", response_model=MachineRead)
def update(
    machine_id: str,
    payload: MachineUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_machine(
        db,
        machine_id=machine_id,
        payload=payload,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )
