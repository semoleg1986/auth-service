from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from src.domain.session.entity import Session
from src.infrastructure.persistence.sqlalchemy.models import SessionModel


class SqlAlchemySessionRepository:
    def __init__(self, db_session: DbSession) -> None:
        self._db = db_session

    def _to_domain(self, model: SessionModel) -> Session:
        return Session(
            token_id=model.token_id,
            user_id=model.user_id,
            expires_at=model.expires_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            revoked_at=model.revoked_at,
            revoke_reason=model.revoke_reason,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            geo_city=model.geo_city,
            geo_region=model.geo_region,
            geo_country=model.geo_country,
            geo_display=model.geo_display,
        )

    def get_by_id(self, token_id: UUID) -> Session | None:
        model = self._db.get(SessionModel, token_id)
        if model is None:
            return None
        return self._to_domain(model)

    def save(self, session: Session) -> None:
        model = self._db.get(SessionModel, session.token_id)
        if model is None:
            model = SessionModel(
                token_id=session.token_id,
                created_at=session.created_at,
            )
            self._db.add(model)

        model.user_id = session.user_id
        model.updated_at = session.updated_at
        model.expires_at = session.expires_at
        model.revoked_at = session.revoked_at
        model.revoke_reason = session.revoke_reason
        model.ip_address = session.ip_address
        model.user_agent = session.user_agent
        model.geo_city = session.geo_city
        model.geo_region = session.geo_region
        model.geo_country = session.geo_country
        model.geo_display = session.geo_display

    def revoke(self, token_id: UUID) -> None:
        session = self.get_by_id(token_id)
        if session is None:
            return
        session.revoke(at=datetime.now(timezone.utc), reason="logout")
        self.save(session)

    def list_by_user(self, user_id: UUID) -> list[Session]:
        rows = self._db.execute(
            select(SessionModel).where(SessionModel.user_id == user_id)
        ).scalars()
        return [self._to_domain(item) for item in rows]

    def revoke_all_by_user(self, user_id: UUID, *, reason: str) -> None:
        now = datetime.now(timezone.utc)
        for session in self.list_by_user(user_id):
            if session.revoked_at is not None:
                continue
            session.revoke(at=now, reason=reason)
            self.save(session)
