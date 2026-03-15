from __future__ import annotations

from typing import Protocol

from src.domain.identity.repository import UserAccountRepository
from src.domain.session.repository import SessionRepository


class UnitOfWork(Protocol):
    user_repo: UserAccountRepository
    session_repo: SessionRepository

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
