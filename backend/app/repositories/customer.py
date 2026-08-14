from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: Session):
        super().__init__(Customer, db)

    def search(self, query: str | None, *, offset: int = 0, limit: int = 100) -> list[Customer]:
        stmt = self.db.query(Customer)
        if query:
            like = f"%{query.strip()}%"
            stmt = stmt.filter(
                or_(
                    Customer.name.ilike(like),
                    Customer.trade_name.ilike(like),
                    Customer.document.ilike(like),
                    Customer.phone.ilike(like),
                    Customer.whatsapp.ilike(like),
                    Customer.email.ilike(like),
                )
            )
        return stmt.order_by(Customer.name.asc()).offset(offset).limit(limit).all()
