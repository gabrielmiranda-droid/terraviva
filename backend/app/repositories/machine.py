from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.machine import Machine
from app.repositories.base import BaseRepository


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
        stmt = self.db.query(Machine)
        if customer_id:
            stmt = stmt.filter(Machine.customer_id == customer_id)
        if query:
            like = f"%{query.strip()}%"
            stmt = stmt.filter(
                or_(
                    Machine.type.ilike(like),
                    Machine.brand.ilike(like),
                    Machine.model.ilike(like),
                    Machine.serial_number.ilike(like),
                    Machine.identification.ilike(like),
                )
            )
        return stmt.order_by(Machine.created_at.desc()).offset(offset).limit(limit).all()
