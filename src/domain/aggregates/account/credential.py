from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from src.domain.errors import InvariantViolationError


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Credential:
    """
    Данные для входа пользователя (credential).

    :param credential_id: Идентификатор credential.
    :type credential_id: UUID
    :param type: Тип credential (password или oauth).
    :type type: str
    :param secret_hash: Хеш пароля (для password).
    :type secret_hash: str | None
    :param provider: OAuth провайдер (для oauth).
    :type provider: str | None
    :param provider_user_id: Идентификатор пользователя у провайдера.
    :type provider_user_id: str | None
    """

    credential_id: UUID
    type: str  # "password" | "oauth"
    secret_hash: str | None = None
    provider: str | None = None
    provider_user_id: str | None = None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    last_used_at: datetime | None = None
    password_changed_at: datetime | None = None
    failed_attempts: int = 0
    locked_until: datetime | None = None

    def __post_init__(self) -> None:
        normalized_type = self.type.strip().lower()
        object.__setattr__(self, "type", normalized_type)

        if self.failed_attempts < 0:
            raise InvariantViolationError("failed_attempts must be >= 0")

        if normalized_type == "password":
            if not self.secret_hash or not self.secret_hash.strip():
                raise InvariantViolationError(
                    "Password credential requires secret_hash"
                )
            if self.provider is not None or self.provider_user_id is not None:
                raise InvariantViolationError(
                    "Password credential cannot have oauth provider fields"
                )
            object.__setattr__(self, "secret_hash", self.secret_hash.strip())
            return

        if normalized_type == "oauth":
            provider = (self.provider or "").strip()
            provider_user_id = (self.provider_user_id or "").strip()
            if not provider or not provider_user_id:
                raise InvariantViolationError(
                    "OAuth credential requires provider and provider_user_id"
                )
            if self.secret_hash is not None and self.secret_hash.strip():
                raise InvariantViolationError(
                    "OAuth credential cannot have secret_hash"
                )
            object.__setattr__(self, "provider", provider)
            object.__setattr__(self, "provider_user_id", provider_user_id)
            object.__setattr__(self, "secret_hash", None)
            return

        raise InvariantViolationError("Unsupported credential type")
