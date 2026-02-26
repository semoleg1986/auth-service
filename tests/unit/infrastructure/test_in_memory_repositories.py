from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.domain.aggregates.account import Session, UserAccount
from src.infrastructure.persistence.repositories.in_memory_session_repository import (
    InMemorySessionRepository,
)
from src.infrastructure.persistence.repositories.in_memory_user_account_repository import (
    InMemoryUserAccountRepository,
)


def test_user_account_repository_crud() -> None:
    repo = InMemoryUserAccountRepository()
    user_id = uuid4()
    account = UserAccount(user_id=user_id, email="user@example.com")

    assert repo.get_by_id(user_id) is None
    repo.save(account)
    assert repo.get_by_id(user_id) is account
    assert repo.get_by_email("user@example.com") is account
    assert repo.get_by_phone("+15550001122") is None


def test_session_repository_save_and_revoke() -> None:
    repo = InMemorySessionRepository()
    token_id = uuid4()
    user_id = uuid4()
    session = Session(
        token_id=token_id,
        user_id=user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )

    assert repo.get_by_id(token_id) is None
    repo.save(session)
    assert repo.get_by_id(token_id) is session

    repo.revoke(token_id)
    assert repo.get_by_id(token_id).revoked_at is not None

    sessions = repo.list_by_user(user_id)
    assert len(sessions) == 1
    assert sessions[0].token_id == token_id
