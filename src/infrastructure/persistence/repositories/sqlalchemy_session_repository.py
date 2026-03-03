from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from src.domain.aggregates.account import Session
from src.infrastructure.persistence.sqlalchemy.models import SessionModel


class SqlAlchemySessionRepository:
    def __init__(self, db_session: DbSession) -> None:
        self._db = db_session

    def _to_domain(self, model: SessionModel) -> Session:
        return Session(
            token_id=model.token_id,
            user_id=model.user_id,
            expires_at=model.expires_at,
            revoked_at=model.revoked_at,
        )

    def get_by_id(self, token_id: UUID) -> Session | None:
        model = self._db.get(SessionModel, token_id)
        if model is None:
            return None
        return self._to_domain(model)

    def save(self, session: Session) -> None:
        model = self._db.get(SessionModel, session.token_id)
        if model is None:
            model = SessionModel(token_id=session.token_id)
            self._db.add(model)

        model.user_id = session.user_id
        model.expires_at = session.expires_at
        model.revoked_at = session.revoked_at

    def revoke(self, token_id: UUID) -> None:
        model = self._db.get(SessionModel, token_id)
        if model is None:
            return
        model.revoked_at = datetime.now(timezone.utc)

    def list_by_user(self, user_id: UUID) -> list[Session]:
        rows = self._db.execute(
            select(SessionModel).where(SessionModel.user_id == user_id)
        ).scalars()
        return [self._to_domain(item) for item in rows]
