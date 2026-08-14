from datetime import UTC, date, datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.enums import BudgetItemType, BudgetStatus, WorkOrderStatus
from app.models.budget import Budget, BudgetItem, BudgetStatusHistory
from app.models.work_order import WorkOrder, WorkOrderStatusHistory
from app.schemas.budget import BudgetDecisionCreate, BudgetUpdate
from app.schemas.operations import WorkshopMachineRead
from app.services.audit import register_audit_log
from app.services.machine_entries import list_machines_in_shop
from app.services.sequences import next_human_number
from app.services.work_orders import get_work_order_detail_or_404, get_work_order_or_404

BUDGET_QUEUE_STATUSES = {
    WorkOrderStatus.AGUARDANDO_DIAGNOSTICO.value,
    WorkOrderStatus.EM_DIAGNOSTICO.value,
    WorkOrderStatus.AGUARDANDO_ORCAMENTO.value,
    WorkOrderStatus.AGUARDANDO_APROVACAO.value,
    WorkOrderStatus.APROVADA.value,
    WorkOrderStatus.RECUSADA.value,
}

ACTIVE_BUDGET_STATUSES = {
    BudgetStatus.RASCUNHO.value,
    BudgetStatus.ENVIADO.value,
    BudgetStatus.AGUARDANDO_RESPOSTA.value,
    BudgetStatus.APROVADO.value,
    BudgetStatus.APROVADO_PARCIALMENTE.value,
}


def list_pending_budgets(
    db: Session,
    *,
    status_filter: str | None,
    search: str | None,
    offset: int,
    limit: int,
) -> list[WorkshopMachineRead]:
    rows: list[WorkshopMachineRead] = []
    statuses = [status_filter] if status_filter else sorted(BUDGET_QUEUE_STATUSES)
    for status_value in statuses:
        if status_value not in BUDGET_QUEUE_STATUSES:
            continue
        rows.extend(
            list_machines_in_shop(
                db,
                search=search,
                status_filter=status_value,
                technician_id=None,
                attendance_type="ORCAMENTO",
                offset=0,
                limit=limit,
            )
        )
    rows.sort(key=lambda item: item.entered_at)
    return rows[offset : offset + limit]


def get_active_budget_for_work_order(db: Session, work_order_id: str) -> Budget | None:
    return (
        db.query(Budget)
        .options(joinedload(Budget.items))
        .filter(Budget.work_order_id == work_order_id, Budget.status.in_(ACTIVE_BUDGET_STATUSES))
        .order_by(Budget.version.desc(), Budget.created_at.desc())
        .first()
    )


def get_budget_or_404(db: Session, budget_id: str) -> Budget:
    budget = db.query(Budget).options(joinedload(Budget.items)).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orcamento nao encontrado.")
    return budget


def create_or_get_budget(
    db: Session,
    *,
    work_order_id: str,
    user_id: str | None,
    ip_address: str | None,
) -> Budget:
    work_order = get_work_order_or_404(db, work_order_id)
    existing = get_active_budget_for_work_order(db, work_order_id)
    if existing:
        return existing

    budget = Budget(
        number=next_human_number(db, Budget, "ORC"),
        work_order_id=work_order.id,
        date=date.today(),
        status=BudgetStatus.RASCUNHO.value,
        responsible_user_id=user_id,
    )
    db.add(budget)
    _set_work_order_status(
        db,
        work_order,
        WorkOrderStatus.AGUARDANDO_ORCAMENTO.value,
        user_id=user_id,
        reason="Orcamento iniciado.",
    )
    db.flush()
    _add_budget_history(db, budget, None, budget.status, user_id, "Orcamento criado.")
    register_audit_log(
        db,
        user_id=user_id,
        action="BUDGET_CREATED",
        entity="budgets",
        entity_id=budget.id,
        after_data={"number": budget.number, "work_order_id": work_order.id},
        ip_address=ip_address,
    )
    db.commit()
    db.refresh(budget)
    return get_budget_or_404(db, budget.id)


def update_budget(
    db: Session,
    *,
    budget_id: str,
    payload: BudgetUpdate,
    user_id: str | None,
    ip_address: str | None,
) -> Budget:
    budget = get_budget_or_404(db, budget_id)
    budget.date = payload.date
    budget.valid_until = payload.valid_until
    budget.notes = payload.notes
    budget.discount = payload.discount
    budget.items.clear()
    db.flush()
    for item in payload.items:
        item_type = item.item_type if item.item_type in {BudgetItemType.PECA.value, BudgetItemType.SERVICO.value} else BudgetItemType.SERVICO.value
        total = (item.quantity * item.unit_price) - item.discount
        budget.items.append(
            BudgetItem(
                item_type=item_type,
                part_id=item.part_id if item_type == BudgetItemType.PECA.value else None,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount=item.discount,
                total=max(total, Decimal("0")),
            )
        )
    _recalculate_budget(budget)
    register_audit_log(
        db,
        user_id=user_id,
        action="BUDGET_UPDATED",
        entity="budgets",
        entity_id=budget.id,
        after_data={"total": str(budget.total), "items": len(payload.items)},
        ip_address=ip_address,
    )
    db.commit()
    return get_budget_or_404(db, budget.id)


def finalize_budget(db: Session, *, budget_id: str, user_id: str | None, ip_address: str | None) -> Budget:
    budget = get_budget_or_404(db, budget_id)
    previous = budget.status
    budget.status = BudgetStatus.AGUARDANDO_RESPOSTA.value
    _add_budget_history(db, budget, previous, budget.status, user_id, "Orcamento finalizado.")
    work_order = get_work_order_or_404(db, budget.work_order_id)
    _set_work_order_status(
        db,
        work_order,
        WorkOrderStatus.AGUARDANDO_APROVACAO.value,
        user_id=user_id,
        reason="Orcamento finalizado e aguardando aprovacao.",
    )
    register_audit_log(db, user_id=user_id, action="BUDGET_FINALIZED", entity="budgets", entity_id=budget.id, ip_address=ip_address)
    db.commit()
    return get_budget_or_404(db, budget.id)


def approve_budget(
    db: Session,
    *,
    budget_id: str,
    payload: BudgetDecisionCreate,
    user_id: str | None,
    ip_address: str | None,
) -> Budget:
    budget = get_budget_or_404(db, budget_id)
    previous = budget.status
    budget.status = BudgetStatus.APROVADO.value
    budget.approval_method = payload.method
    budget.approved_at = datetime.now(UTC)
    budget.responsible_user_id = user_id
    _add_budget_history(db, budget, previous, budget.status, user_id, payload.note or "Orcamento aprovado.")
    work_order = get_work_order_or_404(db, budget.work_order_id)
    _set_work_order_status(db, work_order, WorkOrderStatus.APROVADA.value, user_id=user_id, reason=payload.note or "Orcamento aprovado.")
    register_audit_log(db, user_id=user_id, action="BUDGET_APPROVED", entity="budgets", entity_id=budget.id, ip_address=ip_address)
    db.commit()
    return get_budget_or_404(db, budget.id)


def reject_budget(
    db: Session,
    *,
    budget_id: str,
    payload: BudgetDecisionCreate,
    user_id: str | None,
    ip_address: str | None,
) -> Budget:
    budget = get_budget_or_404(db, budget_id)
    previous = budget.status
    budget.status = BudgetStatus.RECUSADO.value
    budget.rejected_at = datetime.now(UTC)
    budget.rejection_reason = payload.reason or payload.note
    budget.responsible_user_id = user_id
    _add_budget_history(db, budget, previous, budget.status, user_id, payload.reason or "Orcamento recusado.")
    work_order = get_work_order_or_404(db, budget.work_order_id)
    _set_work_order_status(db, work_order, WorkOrderStatus.RECUSADA.value, user_id=user_id, reason=payload.reason or "Orcamento recusado.")
    register_audit_log(db, user_id=user_id, action="BUDGET_REJECTED", entity="budgets", entity_id=budget.id, ip_address=ip_address)
    db.commit()
    return get_budget_or_404(db, budget.id)


def _recalculate_budget(budget: Budget) -> None:
    budget.parts_subtotal = sum((item.total for item in budget.items if item.item_type == BudgetItemType.PECA.value), Decimal("0"))
    budget.services_subtotal = sum((item.total for item in budget.items if item.item_type == BudgetItemType.SERVICO.value), Decimal("0"))
    budget.total = max(budget.parts_subtotal + budget.services_subtotal - budget.discount, Decimal("0"))


def _add_budget_history(
    db: Session,
    budget: Budget,
    from_status: str | None,
    to_status: str,
    user_id: str | None,
    reason: str | None,
) -> None:
    db.add(
        BudgetStatusHistory(
            budget_id=budget.id,
            from_status=from_status,
            to_status=to_status,
            changed_by_user_id=user_id,
            changed_at=datetime.now(UTC),
            reason=reason,
        )
    )


def _set_work_order_status(
    db: Session,
    work_order: WorkOrder,
    status_value: str,
    *,
    user_id: str | None,
    reason: str | None,
) -> None:
    if work_order.status == status_value:
        return
    previous = work_order.status
    work_order.status = status_value
    db.add(
        WorkOrderStatusHistory(
            work_order_id=work_order.id,
            from_status=previous,
            to_status=status_value,
            changed_by_user_id=user_id,
            changed_at=datetime.now(UTC),
            reason=reason,
        )
    )
