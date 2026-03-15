from __future__ import annotations

from typing import Protocol

from src.domain.identity.user_account_repository import UserAccountRepository
from src.domain.session.session_repository import SessionRepository


class UnitOfWork(Protocol):
    user_repo: UserAccountRepository
    session_repo: SessionRepository

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
