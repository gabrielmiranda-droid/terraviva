from datetime import UTC, datetime
from secrets import token_urlsafe

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.enums import AttendanceType, MachineEntryStatus, WorkOrderStatus
from app.models.customer import Customer
from app.models.machine import Machine
from app.models.machine_entry import MachineEntry
from app.models.user import User
from app.models.work_order import WorkOrder, WorkOrderStatusHistory
from app.schemas.machine_entry import MachineEntryCreate, MachineEntryDeliveryCreate
from app.schemas.operations import WorkshopMachineRead
from app.services.audit import register_audit_log
from app.services.customers import get_customer_or_404
from app.services.machines import get_machine_or_404
from app.services.sequences import next_human_number


def list_machine_entries(db: Session, *, offset: int, limit: int) -> list[MachineEntry]:
    return (
        db.query(MachineEntry)
        .order_by(MachineEntry.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def generate_public_token(db: Session) -> str:
    for _ in range(10):
        token = token_urlsafe(24)
        exists = db.query(MachineEntry.id).filter(MachineEntry.public_token == token).first()
        if not exists:
            return token
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Nao foi possivel gerar token publico da entrada.",
    )


def create_machine_entry_with_work_order(
    db: Session,
    *,
    payload: MachineEntryCreate,
    user_id: str | None,
    ip_address: str | None,
) -> tuple[MachineEntry, WorkOrder]:
    customer = get_customer_or_404(db, payload.customer_id)
    machine = get_machine_or_404(db, payload.machine_id)
    if machine.customer_id != customer.id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A maquina selecionada nao pertence ao cliente informado.",
        )

    now = datetime.now(UTC)
    entry = MachineEntry(
        number=next_human_number(db, MachineEntry, "ENT"),
        public_token=generate_public_token(db),
        customer_id=payload.customer_id,
        machine_id=payload.machine_id,
        reported_problem=payload.reported_problem,
        attendance_type=payload.attendance_type.value,
        notes=payload.notes,
        received_by_user_id=user_id,
        accessories=payload.accessories,
        visual_condition=payload.visual_condition,
        status=MachineEntryStatus.OS_CRIADA.value,
    )
    db.add(entry)
    db.flush()

    initial_status = (
        WorkOrderStatus.AGUARDANDO_DIAGNOSTICO.value
        if payload.attendance_type == AttendanceType.ORCAMENTO
        else WorkOrderStatus.APROVADA.value
    )
    work_order = WorkOrder(
        number=next_human_number(db, WorkOrder, "OS"),
        entry_id=entry.id,
        customer_id=payload.customer_id,
        machine_id=payload.machine_id,
        reported_problem=payload.reported_problem,
        status=initial_status,
        opened_at=now,
    )
    db.add(work_order)
    db.flush()
    db.add(
        WorkOrderStatusHistory(
            work_order_id=work_order.id,
            from_status=None,
            to_status=initial_status,
            changed_by_user_id=user_id,
            changed_at=now,
            reason="OS criada a partir da entrada da maquina.",
        )
    )
    register_audit_log(
        db,
        user_id=user_id,
        action="MACHINE_ENTRY_CREATED",
        entity="machine_entries",
        entity_id=entry.id,
        after_data={
            "number": entry.number,
            "customer_id": entry.customer_id,
            "machine_id": entry.machine_id,
            "attendance_type": entry.attendance_type,
        },
        ip_address=ip_address,
    )
    register_audit_log(
        db,
        user_id=user_id,
        action="WORK_ORDER_CREATED",
        entity="work_orders",
        entity_id=work_order.id,
        after_data={"number": work_order.number, "status": work_order.status},
        ip_address=ip_address,
    )
    db.commit()
    db.refresh(entry)
    db.refresh(work_order)
    return entry, work_order


def list_machines_in_shop(
    db: Session,
    *,
    search: str | None,
    status_filter: str | None,
    technician_id: str | None,
    attendance_type: str | None,
    offset: int,
    limit: int,
) -> list[WorkshopMachineRead]:
    query = (
        db.query(MachineEntry, WorkOrder, Customer, Machine, User)
        .join(WorkOrder, WorkOrder.entry_id == MachineEntry.id)
        .join(Customer, Customer.id == MachineEntry.customer_id)
        .join(Machine, Machine.id == MachineEntry.machine_id)
        .outerjoin(User, User.id == WorkOrder.technician_id)
        .filter(MachineEntry.delivered_at.is_(None))
    )
    if status_filter:
        query = query.filter(WorkOrder.status == status_filter)
    if technician_id:
        query = query.filter(WorkOrder.technician_id == technician_id)
    if attendance_type:
        query = query.filter(MachineEntry.attendance_type == attendance_type)
    if search:
        like = f"%{search.strip()}%"
        query = query.filter(
            or_(
                MachineEntry.number.ilike(like),
                WorkOrder.number.ilike(like),
                Customer.name.ilike(like),
                Customer.document.ilike(like),
                Customer.phone.ilike(like),
                Customer.whatsapp.ilike(like),
                Machine.type.ilike(like),
                Machine.brand.ilike(like),
                Machine.model.ilike(like),
                Machine.serial_number.ilike(like),
                Machine.identification.ilike(like),
            )
        )

    rows = (
        query.order_by(MachineEntry.entry_date.asc(), MachineEntry.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    now = datetime.now(UTC)
    result: list[WorkshopMachineRead] = []
    for entry, work_order, customer, machine, technician in rows:
        entered_at = entry.entry_date
        if entered_at.tzinfo is None:
            entered_at = entered_at.replace(tzinfo=UTC)
        days_in_shop = max((now - entered_at).days, 0) if entered_at else 0
        result.append(
            WorkshopMachineRead(
                entry_id=entry.id,
                entry_number=entry.number,
                entry_public_token=entry.public_token,
                work_order_id=work_order.id,
                work_order_number=work_order.number,
                customer_id=customer.id,
                customer_name=customer.name,
                customer_phone=customer.whatsapp or customer.phone,
                machine_id=machine.id,
                machine_type=machine.type,
                machine_brand=machine.brand,
                machine_model=machine.model,
                machine_serial_number=machine.serial_number,
                entered_at=entered_at,
                days_in_shop=days_in_shop,
                attendance_type=entry.attendance_type,
                status=work_order.status,
                technician_id=work_order.technician_id,
                technician_name=technician.full_name if technician else None,
                reported_problem=work_order.reported_problem,
            )
        )
    return result


def get_machine_entry_or_404(db: Session, entry_id: str) -> MachineEntry:
    entry = db.query(MachineEntry).filter(MachineEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrada nao encontrada.")
    return entry


def mark_machine_entry_delivered(
    db: Session,
    *,
    entry_id: str,
    payload: MachineEntryDeliveryCreate,
    user_id: str | None,
    ip_address: str | None,
) -> MachineEntry:
    entry = get_machine_entry_or_404(db, entry_id)
    if entry.delivered_at:
        return entry
    now = datetime.now(UTC)
    entry.delivered_at = now
    entry.delivered_by_user_id = user_id
    entry.receiver_name = payload.receiver_name
    entry.delivery_notes = payload.delivery_notes
    entry.status = MachineEntryStatus.ENTREGUE.value
    work_order = db.query(WorkOrder).filter(WorkOrder.entry_id == entry.id).first()
    if work_order and work_order.status != WorkOrderStatus.ENTREGUE.value:
        previous_status = work_order.status
        work_order.status = WorkOrderStatus.ENTREGUE.value
        work_order.delivered_at = now
        db.add(
            WorkOrderStatusHistory(
                work_order_id=work_order.id,
                from_status=previous_status,
                to_status=WorkOrderStatus.ENTREGUE.value,
                changed_by_user_id=user_id,
                changed_at=now,
                reason="Maquina entregue ao cliente.",
            )
        )
    register_audit_log(
        db,
        user_id=user_id,
        action="MACHINE_ENTRY_DELIVERED",
        entity="machine_entries",
        entity_id=entry.id,
        after_data={
            "number": entry.number,
            "delivered_at": now.isoformat(),
            "receiver_name": entry.receiver_name,
        },
        ip_address=ip_address,
    )
    db.commit()
    db.refresh(entry)
    return entry
