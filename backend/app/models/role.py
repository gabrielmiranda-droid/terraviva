from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Role(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))

    users: Mapped[list["User"]] = relationship(back_populates="role")
