from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.domain.aggregates.account import Session


class SessionRepository(Protocol):
    """
    Репозиторий Session.
    """

    def get_by_id(self, token_id: UUID) -> Session | None:
        """
        Получить сессию по id.

        :param token_id: Идентификатор сессии.
        :type token_id: UUID
        :return: Session или None.
        :rtype: Session | None
        """
        ...

    def save(self, session: Session) -> None:
        """
        Сохранить сессию.

        :param session: Session.
        :type session: Session
        :return: None
        :rtype: None
        """
        ...

    def revoke(self, token_id: UUID) -> None:
        """
        Отозвать сессию.

        :param token_id: Идентификатор сессии.
        :type token_id: UUID
        :return: None
        :rtype: None
        """
        ...

    def list_by_user(self, user_id: UUID) -> list[Session]:
        """
        Получить список сессий пользователя.

        :param user_id: Идентификатор пользователя.
        :type user_id: UUID
        :return: Список сессий.
        :rtype: list[Session]
        """
        ...

    def revoke_all_by_user(self, user_id: UUID, *, reason: str) -> None:
        """
        Отозвать все сессии пользователя.

        :param user_id: Идентификатор пользователя.
        :type user_id: UUID
        :param reason: Причина отзыва.
        :type reason: str
        :return: None
        :rtype: None
        """
        ...
