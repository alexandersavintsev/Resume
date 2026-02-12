from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session

from infra.db.models import MatchingTaskORM, PredictionHistoryORM


def create_task(session: Session, *, user_id: uuid.UUID, keywords: list[str]) -> uuid.UUID:
    task = MatchingTaskORM(user_id=user_id, keywords=keywords, is_completed=0)
    session.add(task)
    session.commit()
    return task.id


def mark_task_completed(session: Session, *, task_id: uuid.UUID) -> None:
    task = session.get(MatchingTaskORM, task_id)
    if not task:
        raise ValueError("task not found")
    task.is_completed = 1
    session.commit()


def add_history_item(
    session: Session,
    *,
    user_id: uuid.UUID,
    task_id: uuid.UUID,
    charged_credits: int,
    status: str,
    invalid_items: list[str] | None = None,
) -> uuid.UUID:
    item = PredictionHistoryORM(
        user_id=user_id,
        task_id=task_id,
        charged_credits=charged_credits,
        status=status,
        invalid_items=invalid_items or [],
    )
    session.add(item)
    session.commit()
    return item.id


def list_history(session: Session, *, user_id: uuid.UUID) -> list[PredictionHistoryORM]:
    q = (
        select(PredictionHistoryORM)
        .where(PredictionHistoryORM.user_id == user_id)
        .order_by(PredictionHistoryORM.created_at.desc())
    )
    return list(session.scalars(q).all())
