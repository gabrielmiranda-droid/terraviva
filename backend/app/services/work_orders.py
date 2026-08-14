from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.enums import WorkOrderStatus
from app.models.work_order import WorkOrder, WorkOrderStatusHistory
from app.repositories.work_order import WorkOrderRepository
from app.schemas.operations import WorkOrderStatusUpdate
from app.services.audit import register_audit_log


def list_work_orders(
    db: Session,
    *,
    status_filter: str | None,
    offset: int,
    limit: int,
) -> list[WorkOrder]:
    return WorkOrderRepository(db).list_by_status(status_filter, offset=offset, limit=limit)


def get_work_order_or_404(db: Session, work_order_id: str) -> WorkOrder:
    work_order = WorkOrderRepository(db).get(work_order_id)
    if not work_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OS nao encontrada.")
    return work_order


def get_work_order_detail_or_404(db: Session, work_order_id: str) -> WorkOrder:
    work_order = (
        db.query(WorkOrder)
        .options(
            joinedload(WorkOrder.entry),
            joinedload(WorkOrder.customer),
            joinedload(WorkOrder.machine),
            joinedload(WorkOrder.status_history),
        )
        .filter(WorkOrder.id == work_order_id)
        .first()
    )
    if not work_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OS nao encontrada.")
    return work_order


def update_work_order_status(
    db: Session,
    *,
    work_order_id: str,
    payload: WorkOrderStatusUpdate,
    user_id: str | None,
    ip_address: str | None,
) -> WorkOrder:
    work_order = get_work_order_or_404(db, work_order_id)
    valid_statuses = {status.value for status in WorkOrderStatus}
    if payload.status not in valid_statuses:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Status invalido.")

    previous_status = work_order.status
    if payload.diagnosis is not None:
        work_order.diagnosis = payload.diagnosis
    if payload.internal_notes is not None:
        work_order.internal_notes = payload.internal_notes

    if previous_status != payload.status:
        now = datetime.now(UTC)
        work_order.status = payload.status
        if payload.status == WorkOrderStatus.EM_MANUTENCAO.value and not work_order.started_at:
            work_order.started_at = now
        if payload.status in {WorkOrderStatus.FINALIZADA.value, WorkOrderStatus.PRONTA_PARA_ENTREGA.value}:
            work_order.completed_at = work_order.completed_at or now
        db.add(
            WorkOrderStatusHistory(
                work_order_id=work_order.id,
                from_status=previous_status,
                to_status=payload.status,
                changed_by_user_id=user_id,
                changed_at=now,
                reason=payload.reason,
            )
        )
        register_audit_log(
            db,
            user_id=user_id,
            action="WORK_ORDER_STATUS_CHANGED",
            entity="work_orders",
            entity_id=work_order.id,
            before_data={"status": previous_status},
            after_data={"status": payload.status, "reason": payload.reason},
            ip_address=ip_address,
        )
    db.commit()
    db.refresh(work_order)
    return work_order
