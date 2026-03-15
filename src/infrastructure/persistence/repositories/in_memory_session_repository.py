from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from src.domain.session.entity import Session


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
            now = datetime.now(timezone.utc)
            session.revoke(at=now, reason="logout")

    def list_by_user(self, user_id: UUID) -> list[Session]:
        return [s for s in self._sessions.values() if s.user_id == user_id]

    def revoke_all_by_user(self, user_id: UUID, *, reason: str) -> None:
        now = datetime.now(timezone.utc)
        for session in self._sessions.values():
            if session.user_id != user_id or session.revoked_at is not None:
                continue
            session.revoke(at=now, reason=reason)
