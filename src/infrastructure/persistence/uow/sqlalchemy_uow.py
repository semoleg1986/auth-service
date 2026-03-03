from __future__ import annotations

from sqlalchemy.orm import Session

from src.application.unit_of_work import UnitOfWork

from ..repositories.sqlalchemy_session_repository import SqlAlchemySessionRepository
from ..repositories.sqlalchemy_user_account_repository import (
    SqlAlchemyUserAccountRepository,
)


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, db_session: Session) -> None:
        self._db = db_session
        self.user_repo = SqlAlchemyUserAccountRepository(db_session)
        self.session_repo = SqlAlchemySessionRepository(db_session)

    def commit(self) -> None:
        self._db.commit()

    def rollback(self) -> None:
        self._db.rollback()

    def close(self) -> None:
        self._db.close()
