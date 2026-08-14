from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import AttendanceType, MachineEntryStatus
from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class MachineEntry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "machine_entries"

    number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), index=True, nullable=False)
    machine_id: Mapped[str] = mapped_column(ForeignKey("machines.id"), index=True, nullable=False)
    entry_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    reported_problem: Mapped[str] = mapped_column(Text, nullable=False)
    attendance_type: Mapped[str] = mapped_column(
        String(30),
        default=AttendanceType.SERVICO_DIRETO.value,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text)
    received_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    accessories: Mapped[str | None] = mapped_column(Text)
    visual_condition: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(30),
        default=MachineEntryStatus.RECEBIDA.value,
        index=True,
        nullable=False,
    )
    public_token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_by_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    receiver_name: Mapped[str | None] = mapped_column(String(180))
    delivery_notes: Mapped[str | None] = mapped_column(Text)

    customer: Mapped["Customer"] = relationship(back_populates="machine_entries")
    machine: Mapped["Machine"] = relationship(back_populates="entries")
    received_by: Mapped["User | None"] = relationship(
        back_populates="received_entries",
        foreign_keys=[received_by_user_id],
    )
    delivered_by: Mapped["User | None"] = relationship(
        foreign_keys=[delivered_by_user_id],
    )
    work_order: Mapped["WorkOrder | None"] = relationship(back_populates="entry")
