from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.domain.identity import UserAccount


class UserAccountRepository(Protocol):
    """
    Репозиторий UserAccount.
    """

    def get_by_id(self, user_id: UUID) -> UserAccount | None:
        """
        Получить аккаунт по id.

        :param user_id: Идентификатор пользователя.
        :type user_id: UUID
        :return: UserAccount или None.
        :rtype: UserAccount | None
        """
        ...

    def get_by_email(self, email: str) -> UserAccount | None:
        """
        Получить аккаунт по email.

        :param email: Email пользователя.
        :type email: str
        :return: UserAccount или None.
        :rtype: UserAccount | None
        """
        ...

    def get_by_phone(self, phone: str) -> UserAccount | None:
        """
        Получить аккаунт по телефону.

        :param phone: Телефон пользователя.
        :type phone: str
        :return: UserAccount или None.
        :rtype: UserAccount | None
        """
        ...

    def save(self, account: UserAccount) -> None:
        """
        Сохранить аккаунт.

        :param account: UserAccount.
        :type account: UserAccount
        :return: None
        :rtype: None
        """
        ...
