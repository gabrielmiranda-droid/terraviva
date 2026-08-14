from datetime import UTC, datetime, time

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.enums import WorkOrderStatus
from app.models.machine_entry import MachineEntry
from app.models.work_order import WorkOrder
from app.schemas.dashboard import DashboardMetrics, WorkshopAttentionItem, WorkshopFlow, WorkshopFlowColumn


FINAL_STATUSES = {
    WorkOrderStatus.ENTREGUE.value,
    WorkOrderStatus.CANCELADA.value,
}


def get_dashboard_metrics(db: Session) -> DashboardMetrics:
    today_start = datetime.combine(datetime.now(UTC).date(), time.min, tzinfo=UTC)
    today_end = datetime.combine(datetime.now(UTC).date(), time.max, tzinfo=UTC)

    open_statuses = [status.value for status in WorkOrderStatus if status.value not in FINAL_STATUSES]
    machines_in_shop = db.query(func.count(WorkOrder.id)).filter(WorkOrder.status.in_(open_statuses)).scalar() or 0
    entries_today = (
        db.query(func.count(MachineEntry.id))
        .filter(MachineEntry.entry_date >= today_start, MachineEntry.entry_date <= today_end)
        .scalar()
        or 0
    )
    open_work_orders = machines_in_shop
    waiting_diagnosis = (
        db.query(func.count(WorkOrder.id))
        .filter(WorkOrder.status.in_([WorkOrderStatus.AGUARDANDO_DIAGNOSTICO.value, WorkOrderStatus.EM_DIAGNOSTICO.value]))
        .scalar()
        or 0
    )
    waiting_approval = (
        db.query(func.count(WorkOrder.id))
        .filter(WorkOrder.status == WorkOrderStatus.AGUARDANDO_APROVACAO.value)
        .scalar()
        or 0
    )
    in_maintenance = (
        db.query(func.count(WorkOrder.id))
        .filter(WorkOrder.status == WorkOrderStatus.EM_MANUTENCAO.value)
        .scalar()
        or 0
    )
    ready_for_pickup = (
        db.query(func.count(WorkOrder.id))
        .filter(WorkOrder.status == WorkOrderStatus.PRONTA_PARA_ENTREGA.value)
        .scalar()
        or 0
    )
    return DashboardMetrics(
        machines_in_shop=machines_in_shop,
        entries_today=entries_today,
        open_work_orders=open_work_orders,
        waiting_diagnosis=waiting_diagnosis,
        waiting_approval=waiting_approval,
        in_maintenance=in_maintenance,
        ready_for_pickup=ready_for_pickup,
    )


def get_workshop_flow(db: Session) -> WorkshopFlow:
    groups = [
        ("RECEBIDAS", "Recebidas", [WorkOrderStatus.RECEBIDA.value, WorkOrderStatus.APROVADA.value]),
        (
            "DIAGNOSTICO",
            "Diagnóstico",
            [WorkOrderStatus.AGUARDANDO_DIAGNOSTICO.value, WorkOrderStatus.EM_DIAGNOSTICO.value],
        ),
        ("AGUARDANDO_APROVACAO", "Aguardando aprovação", [WorkOrderStatus.AGUARDANDO_APROVACAO.value]),
        (
            "MANUTENCAO",
            "Manutenção",
            [WorkOrderStatus.AGUARDANDO_PECA.value, WorkOrderStatus.EM_MANUTENCAO.value],
        ),
        ("PRONTAS", "Prontas", [WorkOrderStatus.FINALIZADA.value, WorkOrderStatus.PRONTA_PARA_ENTREGA.value]),
    ]
    columns = [
        WorkshopFlowColumn(
            key=key,
            label=label,
            count=db.query(func.count(WorkOrder.id)).filter(WorkOrder.status.in_(statuses)).scalar() or 0,
        )
        for key, label, statuses in groups
    ]
    rows = (
        db.query(WorkOrder)
        .join(WorkOrder.entry)
        .join(WorkOrder.customer)
        .join(WorkOrder.machine)
        .filter(WorkOrder.status.notin_(FINAL_STATUSES), MachineEntry.delivered_at.is_(None))
        .order_by(MachineEntry.entry_date.asc())
        .limit(8)
        .all()
    )
    now = datetime.now(UTC)
    attention = []
    for work_order in rows:
        entry = work_order.entry
        entry_date = entry.entry_date
        if entry_date.tzinfo is None:
            entry_date = entry_date.replace(tzinfo=UTC)
        machine = work_order.machine
        attention.append(
            WorkshopAttentionItem(
                entry_id=entry.id,
                entry_number=entry.number,
                work_order_id=work_order.id,
                work_order_number=work_order.number,
                customer_name=work_order.customer.name,
                machine_label=" ".join(
                    value for value in [machine.type, machine.brand, machine.model] if value
                ),
                status=work_order.status,
                days_in_shop=max((now - entry_date).days, 0),
                reported_problem=work_order.reported_problem,
            )
        )
    return WorkshopFlow(columns=columns, attention=attention)
