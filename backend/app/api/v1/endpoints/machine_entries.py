from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.enums import PrintDocumentType
from app.models.user import User
from app.schemas.machine_entry import MachineEntryCreate, MachineEntryDeliveryCreate, MachineEntryRead, MachineEntryWithWorkOrder
from app.schemas.operations import PrintJobCreate, PrintJobRead, WorkshopMachineRead
from app.services.machine_entries import (
    create_machine_entry_with_work_order,
    get_machine_entry_or_404,
    list_machine_entries,
    list_machines_in_shop,
    mark_machine_entry_delivered,
)
from app.services.print_jobs import create_print_job

router = APIRouter()


@router.get("", response_model=list[MachineEntryRead])
def list_(
    offset: int = 0,
    limit: int = Query(default=100, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_machine_entries(db, offset=offset, limit=limit)


@router.get("/in-shop", response_model=list[WorkshopMachineRead])
def in_shop(
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    technician_id: str | None = Query(default=None),
    attendance_type: str | None = Query(default=None),
    offset: int = 0,
    limit: int = Query(default=100, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_machines_in_shop(
        db,
        search=search,
        status_filter=status,
        technician_id=technician_id,
        attendance_type=attendance_type,
        offset=offset,
        limit=limit,
    )


@router.post("", response_model=MachineEntryWithWorkOrder, status_code=201)
def create(
    payload: MachineEntryCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry, work_order = create_machine_entry_with_work_order(
        db,
        payload=payload,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )
    return {
        "entry": entry,
        "work_order_id": work_order.id,
        "work_order_number": work_order.number,
    }


@router.get("/{entry_id}", response_model=MachineEntryRead)
def get(entry_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_machine_entry_or_404(db, entry_id)


@router.post("/{entry_id}/deliver", response_model=MachineEntryRead)
def deliver(
    entry_id: str,
    payload: MachineEntryDeliveryCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return mark_machine_entry_delivered(
        db,
        entry_id=entry_id,
        payload=payload,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )


@router.post("/{entry_id}/print-jobs", response_model=PrintJobRead, status_code=201)
def print_entry_document(
    entry_id: str,
    payload: PrintJobCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_machine_entry_or_404(db, entry_id)
    if payload.document_type not in {
        PrintDocumentType.CUSTOMER_ENTRY_RECEIPT,
        PrintDocumentType.MACHINE_TAG,
    }:
        payload = payload.model_copy(update={"document_type": PrintDocumentType.CUSTOMER_ENTRY_RECEIPT})
    return create_print_job(
        db,
        payload=payload,
        reference_type="machine_entries",
        reference_id=entry_id,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )
