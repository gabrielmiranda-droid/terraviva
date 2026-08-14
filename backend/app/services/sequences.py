from sqlalchemy import func
from sqlalchemy.orm import Session


def next_human_number(db: Session, model: type, prefix: str, width: int = 6) -> str:
    count = db.query(func.count(model.id)).scalar() or 0
    return f"{prefix}-{count + 1:0{width}d}"
