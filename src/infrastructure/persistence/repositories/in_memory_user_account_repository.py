from __future__ import annotations

from uuid import UUID

from src.domain.aggregates.account import UserAccount


class InMemoryUserAccountRepository:
    def __init__(self) -> None:
        self._users: dict[UUID, UserAccount] = {}

    def get_by_id(self, user_id: UUID) -> UserAccount | None:
        return self._users.get(user_id)

    def get_by_email(self, email: str) -> UserAccount | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def get_by_phone(self, phone: str) -> UserAccount | None:
        for user in self._users.values():
            if user.phone == phone:
                return user
        return None

    def save(self, account: UserAccount) -> None:
        self._users[account.user_id] = account
