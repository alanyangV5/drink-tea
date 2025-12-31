from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Tea(Base):
    __tablename__ = "tea"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(50))
    year: Mapped[int] = mapped_column(Integer)
    origin: Mapped[str] = mapped_column(String(200))
    spec: Mapped[str] = mapped_column(String(80))

    price_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    price_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    intro: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    cover_url: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="online")
    weight: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anon_user_id: Mapped[str] = mapped_column(String(64))
    tea_id: Mapped[int] = mapped_column(Integer, ForeignKey("tea.id"))
    type: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anon_user_id: Mapped[str] = mapped_column(String(64))
    tea_id: Mapped[int] = mapped_column(Integer, ForeignKey("tea.id"))
    action: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MessageFeedback(Base):
    __tablename__ = "message_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anon_user_id: Mapped[str] = mapped_column(String(64))
    tea_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tea.id"), nullable=True)
    message: Mapped[str] = mapped_column(Text)
    contact: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
