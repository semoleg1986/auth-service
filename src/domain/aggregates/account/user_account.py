from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from src.domain.errors import InvariantViolationError
from src.domain.value_objects import AccountStatus, Role

from .credential import Credential


@dataclass
class UserAccount:
    user_id: UUID
    email: str | None = None
    phone: str | None = None
    status: AccountStatus = AccountStatus.ACTIVE
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

    def block(self) -> None:
        """
        Заблокировать аккаунт.
        """
        self.status = AccountStatus.BLOCKED

    def unblock(self) -> None:
        """
        Разблокировать аккаунт.
        """
        self.status = AccountStatus.ACTIVE

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
