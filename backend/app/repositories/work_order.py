from sqlalchemy.orm import Session

from app.models.work_order import WorkOrder
from app.repositories.base import BaseRepository


class WorkOrderRepository(BaseRepository[WorkOrder]):
    def __init__(self, db: Session):
        super().__init__(WorkOrder, db)

    def list_by_status(
        self,
        status: str | None,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[WorkOrder]:
        stmt = self.db.query(WorkOrder)
        if status:
            stmt = stmt.filter(WorkOrder.status == status)
        return stmt.order_by(WorkOrder.created_at.desc()).offset(offset).limit(limit).all()
