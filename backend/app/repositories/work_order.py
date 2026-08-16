from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.customer import Customer
from app.models.machine import Machine
from app.models.work_order import WorkOrder
from app.repositories.base import BaseRepository


def _search_terms(query: str) -> list[str]:
    clean_query = query.strip()
    digits = "".join(char for char in clean_query if char.isdigit())
    terms = [clean_query]
    if digits and digits != clean_query:
        terms.append(digits)
    return terms


class WorkOrderRepository(BaseRepository[WorkOrder]):
    def __init__(self, db: Session):
        super().__init__(WorkOrder, db)

    def list_by_status(
        self,
        status: str | None,
        *,
        search: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[WorkOrder]:
        stmt = self.db.query(WorkOrder).options(joinedload(WorkOrder.customer), joinedload(WorkOrder.machine))
        if status:
            stmt = stmt.filter(WorkOrder.status == status)
        if search:
            stmt = stmt.join(Customer, Customer.id == WorkOrder.customer_id).join(
                Machine,
                Machine.id == WorkOrder.machine_id,
            )
            filters = []
            for term in _search_terms(search):
                like = f"%{term}%"
                filters.extend(
                    [
                        WorkOrder.number.ilike(like),
                        WorkOrder.reported_problem.ilike(like),
                        WorkOrder.diagnosis.ilike(like),
                        Customer.name.ilike(like),
                        Customer.trade_name.ilike(like),
                        Customer.document.ilike(like),
                        Customer.phone.ilike(like),
                        Customer.whatsapp.ilike(like),
                        Machine.type.ilike(like),
                        Machine.brand.ilike(like),
                        Machine.model.ilike(like),
                        Machine.serial_number.ilike(like),
                        Machine.identification.ilike(like),
                    ]
                )
            stmt = stmt.filter(or_(*filters))
        return stmt.order_by(WorkOrder.created_at.desc()).offset(offset).limit(limit).all()
