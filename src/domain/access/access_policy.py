from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from src.domain.access.role import ROLE_ADMIN, ROLE_AUDITOR, ROLE_SUPPORT
from src.domain.identity import AccountStatus, UserAccount
from src.domain.session import Session


@dataclass(frozen=True)
class Actor:
    """
    Контекст действия (актор).

    :param user_id: Идентификатор актёра.
    :type user_id: UUID
    :param is_admin: Legacy-флаг администратора (для обратной совместимости).
    :type is_admin: bool
    :param roles: Роли актёра.
    :type roles: frozenset[str]
    """

    user_id: UUID
    is_admin: bool = False
    roles: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        normalized_roles = {r.strip().lower() for r in self.roles if r.strip()}
        if self.is_admin:
            normalized_roles.add(ROLE_ADMIN)
        object.__setattr__(self, "roles", frozenset(normalized_roles))
        object.__setattr__(self, "is_admin", ROLE_ADMIN in normalized_roles)

    def has_role(self, role_name: str) -> bool:
        return role_name in self.roles


class AccessPolicy:
    """
    Политики доступа для auth домена.
    """

    @staticmethod
    def can_assign_role(actor: Actor, account: UserAccount) -> bool:
        """
        Может ли актор назначать роли.

        :param actor: Актор.
        :type actor: Actor
        :param account: Аккаунт.
        :type account: UserAccount
        :return: True, если доступ разрешён.
        :rtype: bool
        """
        return actor.has_role(ROLE_ADMIN)

    @staticmethod
    def can_block_user(actor: Actor, account: UserAccount) -> bool:
        """
        Может ли актор блокировать пользователя.

        :param actor: Актор.
        :type actor: Actor
        :param account: Аккаунт.
        :type account: UserAccount
        :return: True, если доступ разрешён.
        :rtype: bool
        """
        return actor.has_role(ROLE_ADMIN)

    @staticmethod
    def can_unblock_user(actor: Actor, account: UserAccount) -> bool:
        """
        Может ли актор разблокировать пользователя.

        :param actor: Актор.
        :type actor: Actor
        :param account: Аккаунт.
        :type account: UserAccount
        :return: True, если доступ разрешён.
        :rtype: bool
        """
        return actor.has_role(ROLE_ADMIN)

    @staticmethod
    def can_view_roles(actor: Actor, account: UserAccount) -> bool:
        """
        Может ли актор просматривать роли пользователя.

        :param actor: Актор.
        :type actor: Actor
        :param account: Аккаунт.
        :type account: UserAccount
        :return: True, если доступ разрешён.
        :rtype: bool
        """
        return (
            actor.user_id == account.user_id
            or actor.has_role(ROLE_ADMIN)
            or actor.has_role(ROLE_AUDITOR)
            or actor.has_role(ROLE_SUPPORT)
        )

    @staticmethod
    def can_view_sessions(actor: Actor, account: UserAccount) -> bool:
        """
        Может ли актор просматривать сессии пользователя.

        :param actor: Актор.
        :type actor: Actor
        :param account: Аккаунт.
        :type account: UserAccount
        :return: True, если доступ разрешён.
        :rtype: bool
        """
        return (
            actor.user_id == account.user_id
            or actor.has_role(ROLE_ADMIN)
            or actor.has_role(ROLE_AUDITOR)
            or actor.has_role(ROLE_SUPPORT)
        )

    @staticmethod
    def can_login(account: UserAccount) -> bool:
        """
        Может ли пользователь логиниться.

        :param account: Аккаунт.
        :type account: UserAccount
        :return: True, если доступ разрешён.
        :rtype: bool
        """
        return account.status == AccountStatus.ACTIVE

    @staticmethod
    def can_refresh(session: Session, *, now) -> bool:
        """
        Может ли сессия быть обновлена.

        :param session: Сессия.
        :type session: Session
        :param now: Текущее время.
        :type now: datetime
        :return: True, если доступ разрешён.
        :rtype: bool
        """
        return session.is_active(now=now)
