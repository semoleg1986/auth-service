from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from uuid import UUID

from src.domain.errors import InvariantViolationError
from src.domain.value_objects import AccountStatus, Role

from .credential import Credential


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class UserAccount:
    user_id: UUID
    email: str | None = None
    phone: str | None = None
    org_id: str | None = None
    status: AccountStatus = AccountStatus.ACTIVE
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    version: int = 1
    last_login_at: datetime | None = None
    blocked_at: datetime | None = None
    status_reason: str | None = None
    roles: set[Role] = field(default_factory=set)
    credentials: list[Credential] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        Проверить инварианты создания аккаунта.

        :raises InvariantViolationError: Если отсутствуют email и phone.
        """
        if not self.email and not self.phone:
            raise InvariantViolationError("UserAccount must have email or phone")

    def assign_role(self, role: Role) -> None:
        """
        Назначить роль аккаунту.

        :param role: Роль.
        :type role: Role
        """
        self.roles.add(role)

    def remove_role(self, role: Role) -> None:
        """
        Удалить роль у аккаунта.

        :param role: Роль.
        :type role: Role
        """
        self.roles.discard(role)

    def block(self, *, at: datetime | None = None, reason: str | None = None) -> None:
        """
        Заблокировать аккаунт.
        """
        now = at or _utcnow()
        self.status = AccountStatus.BLOCKED
        self.blocked_at = now
        self.status_reason = reason
        self.updated_at = now

    def unblock(self, *, at: datetime | None = None) -> None:
        """
        Разблокировать аккаунт.
        """
        now = at or _utcnow()
        self.status = AccountStatus.ACTIVE
        self.blocked_at = None
        self.status_reason = None
        self.updated_at = now

    def mark_login(self, *, at: datetime | None = None) -> None:
        """
        Зафиксировать успешный логин аккаунта.
        """
        now = at or _utcnow()
        self.last_login_at = now
        self.updated_at = now

    def add_credential(self, credential: Credential) -> None:
        """
        Добавить credential к аккаунту.

        :param credential: Credential.
        :type credential: Credential
        :raises InvariantViolationError: Если тип credential не поддержан/существует.
        """
        if any(c.type == credential.type for c in self.credentials):
            raise InvariantViolationError("Credential type already exists")
        self.credentials.append(credential)

    def get_password_credential(self) -> Credential | None:
        return next((c for c in self.credentials if c.type == "password"), None)

    def is_password_locked(self, *, at: datetime | None = None) -> bool:
        credential = self.get_password_credential()
        if credential is None or credential.locked_until is None:
            return False
        now = at or _utcnow()
        return credential.locked_until > now

    def register_failed_password_attempt(
        self,
        *,
        at: datetime | None = None,
        lock_threshold: int = 5,
        lock_ttl_seconds: int = 900,
    ) -> None:
        credential = self.get_password_credential()
        if credential is None:
            raise InvariantViolationError("Password credential not found")
        now = at or _utcnow()
        next_failed = credential.failed_attempts + 1
        locked_until = credential.locked_until
        if next_failed >= lock_threshold:
            locked_until = now + timedelta(seconds=lock_ttl_seconds)
        self._replace_credential(
            replace(
                credential,
                failed_attempts=next_failed,
                locked_until=locked_until,
                updated_at=now,
            )
        )
        self.updated_at = now

    def register_successful_password_login(self, *, at: datetime | None = None) -> None:
        credential = self.get_password_credential()
        if credential is None:
            raise InvariantViolationError("Password credential not found")
        now = at or _utcnow()
        self._replace_credential(
            replace(
                credential,
                failed_attempts=0,
                locked_until=None,
                last_used_at=now,
                updated_at=now,
            )
        )
        self.updated_at = now

    def _replace_credential(self, updated_credential: Credential) -> None:
        self.credentials = [
            updated_credential
            if credential.credential_id == updated_credential.credential_id
            else credential
            for credential in self.credentials
        ]
