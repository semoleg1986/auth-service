from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Session:
    """
    Сессия (refresh token).

    :param token_id: Идентификатор сессии.
    :type token_id: UUID
    :param user_id: Идентификатор пользователя.
    :type user_id: UUID
    :param expires_at: Время истечения.
    :type expires_at: datetime
    :param revoked_at: Время отзыва.
    :type revoked_at: datetime | None
    """

    token_id: UUID
    user_id: UUID
    expires_at: datetime
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    revoked_at: datetime | None = None
    revoke_reason: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None

    def revoke(self, *, at: datetime, reason: str | None = None) -> None:
        """
        Отозвать сессию.

        :param at: Время отзыва.
        :type at: datetime
        """
        self.revoked_at = at
        self.revoke_reason = reason
        self.updated_at = at

    def is_active(self, *, now: datetime) -> bool:
        """
        Проверить активность сессии.

        :param now: Текущее время.
        :type now: datetime
        :return: True, если сессия активна.
        :rtype: bool
        """
        if self.revoked_at is not None:
            return False
        return now < self.expires_at
