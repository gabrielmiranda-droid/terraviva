from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.customer import Customer
from app.models.machine import Machine
from app.repositories.base import BaseRepository


def _search_terms(query: str) -> list[str]:
    clean_query = query.strip()
    digits = "".join(char for char in clean_query if char.isdigit())
    terms = [clean_query]
    if digits and digits != clean_query:
        terms.append(digits)
    return terms


class MachineRepository(BaseRepository[Machine]):
    def __init__(self, db: Session):
        super().__init__(Machine, db)

    def search(
        self,
        query: str | None,
        *,
        customer_id: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Machine]:
        stmt = self.db.query(Machine).options(joinedload(Machine.customer))
        if customer_id:
            stmt = stmt.filter(Machine.customer_id == customer_id)
        if query:
            stmt = stmt.outerjoin(Customer, Customer.id == Machine.customer_id)
            filters = []
            for term in _search_terms(query):
                like = f"%{term}%"
                filters.extend(
                    [
                        Machine.type.ilike(like),
                        Machine.brand.ilike(like),
                        Machine.model.ilike(like),
                        Machine.serial_number.ilike(like),
                        Machine.identification.ilike(like),
                        Customer.name.ilike(like),
                        Customer.trade_name.ilike(like),
                        Customer.document.ilike(like),
                        Customer.phone.ilike(like),
                        Customer.whatsapp.ilike(like),
                    ]
                )
            stmt = stmt.filter(or_(*filters))
        return stmt.order_by(Machine.created_at.desc()).offset(offset).limit(limit).all()
