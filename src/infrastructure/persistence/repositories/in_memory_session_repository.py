from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from src.domain.aggregates.account import Session


class InMemorySessionRepository:
    def __init__(self) -> None:
        self._sessions: dict[UUID, Session] = {}

    def get_by_id(self, token_id: UUID) -> Session | None:
        return self._sessions.get(token_id)

    def save(self, session: Session) -> None:
        self._sessions[session.token_id] = session

    def revoke(self, token_id: UUID) -> None:
        session = self._sessions.get(token_id)
        if session is not None:
            session.revoked_at = datetime.now(timezone.utc)

    def list_by_user(self, user_id: UUID) -> list[Session]:
        return [s for s in self._sessions.values() if s.user_id == user_id]
