from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.erp_product import ErpProductRead, ErpProductSummary
from app.services.database import get_database_mode
from app.services.erp_products import get_erp_product_summary, list_erp_products

router = APIRouter()


@router.get("", response_model=list[ErpProductRead])
def list_products(
    search: str | None = Query(default=None),
    offset: int = 0,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if get_database_mode() == "sqlite":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Produtos reais estao no Supabase. Preencha DATABASE_URL com a senha real e reinicie o backend sem dev_sqlite.py.",
        )
    return list_erp_products(db, search=search, offset=offset, limit=limit)


@router.get("/summary", response_model=ErpProductSummary)
def product_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if get_database_mode() == "sqlite":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Resumo de produtos reais esta no Supabase. Preencha DATABASE_URL com a senha real e reinicie o backend sem dev_sqlite.py.",
        )
    return get_erp_product_summary(db)
