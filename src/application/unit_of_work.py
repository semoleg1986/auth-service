from __future__ import annotations

from typing import Protocol

from src.domain.repositories.session_repository import SessionRepository
from src.domain.repositories.user_account_repository import UserAccountRepository


class UnitOfWork(Protocol):
    user_repo: UserAccountRepository
    session_repo: SessionRepository

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
