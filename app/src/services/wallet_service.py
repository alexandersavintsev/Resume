from __future__ import annotations

import uuid
from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.db.models import UserORM, BalanceORM, TransactionORM


class NotFoundError(Exception):
    pass


class InsufficientBalanceError(Exception):
    pass


@dataclass(frozen=True)
class TxResult:
    tx_id: uuid.UUID
    new_balance: int


def create_user(session: Session, *, email: str, role: str, initial_credits: int = 0) -> uuid.UUID:
    user = session.scalar(select(UserORM).where(UserORM.email == email))
    if user:
        return user.id

    user = UserORM(email=email, role=role)
    session.add(user)
    session.flush()
    session.add(BalanceORM(user_id=user.id, credits=initial_credits))
    session.commit()
    return user.id


def top_up(session: Session, *, user_id: uuid.UUID, amount: int, task_id: uuid.UUID | None = None) -> TxResult:
    if amount <= 0:
        raise ValueError("amount must be positive")

    with session.begin():
        bal = session.get(BalanceORM, user_id)
        if not bal:
            raise NotFoundError("balance not found")

        bal.credits += amount
        tx = TransactionORM(user_id=user_id, tx_type="top_up", amount_credits=amount, task_id=task_id)
        session.add(tx)
        session.flush()

        return TxResult(tx_id=tx.id, new_balance=bal.credits)


def charge(session: Session, *, user_id: uuid.UUID, amount: int, task_id: uuid.UUID | None = None) -> TxResult:
    if amount <= 0:
        raise ValueError("amount must be positive")

    with session.begin():
        bal = session.get(BalanceORM, user_id)
        if not bal:
            raise NotFoundError("balance not found")

        if bal.credits < amount:
            raise InsufficientBalanceError("insufficient balance")

        bal.credits -= amount
        tx = TransactionORM(user_id=user_id, tx_type="charge", amount_credits=amount, task_id=task_id)
        session.add(tx)
        session.flush()

        return TxResult(tx_id=tx.id, new_balance=bal.credits)


def list_transactions(session: Session, *, user_id: uuid.UUID) -> list[TransactionORM]:
    q = (
        select(TransactionORM)
        .where(TransactionORM.user_id == user_id)
        .order_by(TransactionORM.created_at.desc())
    )
    return list(session.scalars(q).all())
