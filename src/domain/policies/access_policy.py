from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from src.domain.aggregates.account import Session, UserAccount
from src.domain.value_objects import AccountStatus


@dataclass(frozen=True)
class Actor:
    """
    Контекст действия (актор).

    :param user_id: Идентификатор актёра.
    :type user_id: UUID
    :param is_admin: Флаг администратора.
    :type is_admin: bool
    """

    user_id: UUID
    is_admin: bool


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
        return actor.is_admin

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
        return actor.is_admin

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
        return actor.is_admin

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
        return actor.is_admin or actor.user_id == account.user_id

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
        return actor.is_admin or actor.user_id == account.user_id

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
