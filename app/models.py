from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import String, Text, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from utils import get_current_naive_dt


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(index=True, unique=True)
    first_name: Mapped[str | None] = mapped_column(String(255), default=None)
    last_name: Mapped[str | None] = mapped_column(String(255), default=None)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, default=None)
    date_of_birth: Mapped[date | None] = mapped_column(default=None)
    about_me: Mapped[str | None] = mapped_column(Text, default=None)
    is_private: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(
        default=get_current_naive_dt, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=get_current_naive_dt,
        server_default=func.now(),
        onupdate=get_current_naive_dt,
    )
