from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
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
        if credential.type not in {"password", "oauth"}:
            raise InvariantViolationError("Unsupported credential type")
        if any(c.type == credential.type for c in self.credentials):
            raise InvariantViolationError("Credential type already exists")
        self.credentials.append(credential)
