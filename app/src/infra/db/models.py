from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    String, Integer, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.db.database import Base


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(32), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, nullable=False)

    balance: Mapped["BalanceORM"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    transactions: Mapped[list["TransactionORM"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    tasks: Mapped[list["MatchingTaskORM"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    history: Mapped[list["PredictionHistoryORM"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class BalanceORM(Base):
    __tablename__ = "balances"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    credits: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user: Mapped["UserORM"] = relationship(back_populates="balance")


class TransactionORM(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    tx_type: Mapped[str] = mapped_column(String(16), nullable=False)  # top_up / charge
    amount_credits: Mapped[int] = mapped_column(Integer, nullable=False)
    task_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, nullable=False, index=True)

    user: Mapped["UserORM"] = relationship(back_populates="transactions")


class MLModelORM(Base):
    __tablename__ = "ml_models"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, nullable=False)


class MatchingTaskORM(Base):
    __tablename__ = "matching_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # query keywords as JSON
    keywords: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, nullable=False, index=True)

    user: Mapped["UserORM"] = relationship(back_populates="tasks")
    history_items: Mapped[list["PredictionHistoryORM"]] = relationship(back_populates="task", cascade="all, delete-orphan")


class PredictionHistoryORM(Base):
    __tablename__ = "prediction_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("matching_tasks.id", ondelete="CASCADE"), nullable=False, index=True)

    charged_credits: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)  # success / failed / partially_valid
    invalid_items: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow, nullable=False, index=True)

    user: Mapped["UserORM"] = relationship(back_populates="history")
    task: Mapped["MatchingTaskORM"] = relationship(back_populates="history_items")

    __table_args__ = (
        UniqueConstraint("id", "user_id", name="uq_history_id_user"),
    )
