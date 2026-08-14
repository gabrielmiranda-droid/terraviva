from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.audit import register_audit_log


def list_customers(db: Session, *, query: str | None, offset: int, limit: int) -> list[Customer]:
    return CustomerRepository(db).search(query, offset=offset, limit=limit)


def get_customer_or_404(db: Session, customer_id: str) -> Customer:
    customer = CustomerRepository(db).get(customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente nao encontrado.")
    return customer


def create_customer(
    db: Session,
    *,
    payload: CustomerCreate,
    user_id: str | None,
    ip_address: str | None,
) -> Customer:
    data = payload.model_dump()
    customer = Customer(**data)
    db.add(customer)
    db.flush()
    register_audit_log(
        db,
        user_id=user_id,
        action="CUSTOMER_CREATED",
        entity="customers",
        entity_id=customer.id,
        after_data=data,
        ip_address=ip_address,
    )
    db.commit()
    db.refresh(customer)
    return customer


def update_customer(
    db: Session,
    *,
    customer_id: str,
    payload: CustomerUpdate,
    user_id: str | None,
    ip_address: str | None,
) -> Customer:
    customer = get_customer_or_404(db, customer_id)
    before = {
        "name": customer.name,
        "document": customer.document,
        "phone": customer.phone,
        "whatsapp": customer.whatsapp,
        "email": customer.email,
        "is_active": customer.is_active,
    }
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(customer, field, value)
    db.flush()
    register_audit_log(
        db,
        user_id=user_id,
        action="CUSTOMER_UPDATED",
        entity="customers",
        entity_id=customer.id,
        before_data=before,
        after_data=data,
        ip_address=ip_address,
    )
    db.commit()
    db.refresh(customer)
    return customer
