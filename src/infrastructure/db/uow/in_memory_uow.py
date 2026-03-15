from __future__ import annotations

from src.application.unit_of_work import UnitOfWork

from ..repositories.in_memory_session_repository import InMemorySessionRepository
from ..repositories.in_memory_user_account_repository import (
    InMemoryUserAccountRepository,
)


class InMemoryUnitOfWork(UnitOfWork):
    def __init__(
        self,
        *,
        user_repo: InMemoryUserAccountRepository | None = None,
        session_repo: InMemorySessionRepository | None = None,
    ) -> None:
        self.user_repo = user_repo or InMemoryUserAccountRepository()
        self.session_repo = session_repo or InMemorySessionRepository()
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True
