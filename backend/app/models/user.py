from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    role_id: Mapped[str | None] = mapped_column(ForeignKey("roles.id"))

    role: Mapped["Role | None"] = relationship(back_populates="users")
    received_entries: Mapped[list["MachineEntry"]] = relationship(
        back_populates="received_by",
        foreign_keys="MachineEntry.received_by_user_id",
    )
    assigned_work_orders: Mapped[list["WorkOrder"]] = relationship(
        back_populates="technician",
        foreign_keys="WorkOrder.technician_id",
    )
