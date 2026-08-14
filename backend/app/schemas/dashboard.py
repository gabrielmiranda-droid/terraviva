from pydantic import BaseModel


class DashboardMetrics(BaseModel):
    machines_in_shop: int
    entries_today: int
    open_work_orders: int
    waiting_diagnosis: int
    waiting_approval: int
    in_maintenance: int
    ready_for_pickup: int


class DatabaseStatus(BaseModel):
    mode: str
    is_supabase: bool
    message: str


class WorkshopFlowColumn(BaseModel):
    key: str
    label: str
    count: int


class WorkshopAttentionItem(BaseModel):
    entry_id: str
    entry_number: str
    work_order_id: str
    work_order_number: str
    customer_name: str
    machine_label: str
    status: str
    days_in_shop: int
    reported_problem: str


class WorkshopFlow(BaseModel):
    columns: list[WorkshopFlowColumn]
    attention: list[WorkshopAttentionItem]
