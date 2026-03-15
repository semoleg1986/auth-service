from __future__ import annotations

from src.domain.access.actor import Actor
from src.domain.access.role import ROLE_ADMIN, ROLE_AUDITOR, ROLE_SUPPORT
from src.domain.identity.entity import UserAccount
from src.domain.identity.value_objects import AccountStatus
from src.domain.session.entity import Session


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
