from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.part import PartCreate, PartSearchRead
from app.services.parts import create_part, list_parts, part_to_search_read

router = APIRouter()


@router.get("", response_model=list[PartSearchRead])
def list_(
    search: str | None = Query(default=None),
    offset: int = 0,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return list_parts(db, search=search, offset=offset, limit=limit)


@router.post("", response_model=PartSearchRead, status_code=201)
def create(
    payload: PartCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return part_to_search_read(create_part(db, payload=payload))
