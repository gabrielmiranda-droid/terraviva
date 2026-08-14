from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.machine import Machine
from app.repositories.machine import MachineRepository
from app.schemas.machine import MachineCreate, MachineUpdate
from app.services.audit import register_audit_log
from app.services.customers import get_customer_or_404


def list_machines(
    db: Session,
    *,
    query: str | None,
    customer_id: str | None,
    offset: int,
    limit: int,
) -> list[Machine]:
    return MachineRepository(db).search(query, customer_id=customer_id, offset=offset, limit=limit)


def get_machine_or_404(db: Session, machine_id: str) -> Machine:
    machine = MachineRepository(db).get(machine_id)
    if not machine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maquina nao encontrada.")
    return machine


def create_machine(
    db: Session,
    *,
    payload: MachineCreate,
    user_id: str | None,
    ip_address: str | None,
) -> Machine:
    get_customer_or_404(db, payload.customer_id)
    data = payload.model_dump()
    machine = Machine(**data)
    db.add(machine)
    db.flush()
    register_audit_log(
        db,
        user_id=user_id,
        action="MACHINE_CREATED",
        entity="machines",
        entity_id=machine.id,
        after_data=data,
        ip_address=ip_address,
    )
    db.commit()
    db.refresh(machine)
    return machine


def update_machine(
    db: Session,
    *,
    machine_id: str,
    payload: MachineUpdate,
    user_id: str | None,
    ip_address: str | None,
) -> Machine:
    machine = get_machine_or_404(db, machine_id)
    data = payload.model_dump(exclude_unset=True)
    if data.get("customer_id"):
        get_customer_or_404(db, data["customer_id"])
    before = {
        "customer_id": machine.customer_id,
        "type": machine.type,
        "brand": machine.brand,
        "model": machine.model,
        "serial_number": machine.serial_number,
        "identification": machine.identification,
        "is_active": machine.is_active,
    }
    for field, value in data.items():
        setattr(machine, field, value)
    db.flush()
    register_audit_log(
        db,
        user_id=user_id,
        action="MACHINE_UPDATED",
        entity="machines",
        entity_id=machine.id,
        before_data=before,
        after_data=data,
        ip_address=ip_address,
    )
    db.commit()
    db.refresh(machine)
    return machine
