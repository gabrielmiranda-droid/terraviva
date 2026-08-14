from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories.base import BaseRepository


def _search_terms(query: str) -> list[str]:
    clean_query = query.strip()
    digits = "".join(char for char in clean_query if char.isdigit())
    terms = [clean_query]
    if digits and digits != clean_query:
        terms.append(digits)
    return terms


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: Session):
        super().__init__(Customer, db)

    def search(self, query: str | None, *, offset: int = 0, limit: int = 100) -> list[Customer]:
        stmt = self.db.query(Customer)
        if query:
            filters = []
            for term in _search_terms(query):
                like = f"%{term}%"
                filters.extend(
                    [
                        Customer.name.ilike(like),
                        Customer.trade_name.ilike(like),
                        Customer.document.ilike(like),
                        Customer.phone.ilike(like),
                        Customer.whatsapp.ilike(like),
                        Customer.email.ilike(like),
                        Customer.legacy_code.ilike(like),
                    ]
                )
            stmt = stmt.filter(or_(*filters))
        return stmt.order_by(Customer.name.asc()).offset(offset).limit(limit).all()
