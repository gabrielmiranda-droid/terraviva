from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import PrintJobStatus
from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class PrintJob(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "print_jobs"

    document_type: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    reference_type: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    reference_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30),
        default=PrintJobStatus.CREATED.value,
        index=True,
        nullable=False,
    )
    printer_name: Mapped[str | None] = mapped_column(String(120))
    printed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    printed_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
