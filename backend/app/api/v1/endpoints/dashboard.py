from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.dashboard import DashboardMetrics, DatabaseStatus, WorkshopFlow
from app.services.database import get_database_mode
from app.services.dashboard import get_dashboard_metrics, get_workshop_flow

router = APIRouter()


@router.get("/metrics", response_model=DashboardMetrics)
def metrics(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> DashboardMetrics:
    return get_dashboard_metrics(db)


@router.get("/database", response_model=DatabaseStatus)
def database_status(current_user=Depends(get_current_user)) -> DatabaseStatus:
    mode = get_database_mode()
    messages = {
        "sqlite": "Rodando com banco local de teste. Produtos reais do Supabase nao aparecem neste modo.",
        "supabase": "Rodando conectado ao Postgres do Supabase.",
        "postgresql": "Rodando conectado a um Postgres externo.",
        "unknown": "Banco de dados nao identificado.",
    }
    return DatabaseStatus(
        mode=mode,
        is_supabase=mode == "supabase",
        message=messages.get(mode, messages["unknown"]),
    )


@router.get("/workshop-flow", response_model=WorkshopFlow)
def workshop_flow(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> WorkshopFlow:
    return get_workshop_flow(db)
