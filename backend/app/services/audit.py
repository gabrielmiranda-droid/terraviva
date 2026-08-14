from datetime import UTC, datetime
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def register_audit_log(
    db: Session,
    *,
    user_id: str | None,
    action: str,
    entity: str,
    entity_id: str | None = None,
    before_data: dict[str, Any] | None = None,
    after_data: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        before_data=jsonable_encoder(before_data) if before_data is not None else None,
        after_data=jsonable_encoder(after_data) if after_data is not None else None,
        ip_address=ip_address,
        occurred_at=datetime.now(UTC),
    )
    db.add(log)
    return log
