from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.services.customers import create_customer, get_customer_or_404, list_customers, update_customer

router = APIRouter()


@router.get("", response_model=list[CustomerRead])
def list_(
    search: str | None = Query(default=None),
    offset: int = 0,
    limit: int = Query(default=100, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_customers(db, query=search, offset=offset, limit=limit)


@router.post("", response_model=CustomerRead, status_code=201)
def create(
    payload: CustomerCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_customer(
        db,
        payload=payload,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )


@router.get("/{customer_id}", response_model=CustomerRead)
def get(customer_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_customer_or_404(db, customer_id)


@router.patch("/{customer_id}", response_model=CustomerRead)
def update(
    customer_id: str,
    payload: CustomerUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_customer(
        db,
        customer_id=customer_id,
        payload=payload,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
    )
