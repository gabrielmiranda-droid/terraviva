from typing import Generic, TypeVar

from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    def __init__(self, model: type[ModelT], db: Session):
        self.model = model
        self.db = db

    def get(self, item_id: str) -> ModelT | None:
        return self.db.get(self.model, item_id)

    def list(self, *, offset: int = 0, limit: int = 100) -> list[ModelT]:
        return self.db.query(self.model).offset(offset).limit(limit).all()

    def add(self, instance: ModelT) -> ModelT:
        self.db.add(instance)
        return instance
