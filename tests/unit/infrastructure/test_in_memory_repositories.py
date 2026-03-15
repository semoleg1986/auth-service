from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.domain.identity.user_account import UserAccount
from src.domain.session.session import Session
from src.infrastructure import InMemorySessionRepository, InMemoryUserAccountRepository


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


def test_session_repository_revoke_all_by_user() -> None:
    repo = InMemorySessionRepository()
    user_id = uuid4()
    first = Session(
        token_id=uuid4(),
        user_id=user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    second = Session(
        token_id=uuid4(),
        user_id=user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    repo.save(first)
    repo.save(second)

    repo.revoke_all_by_user(user_id, reason="security_test")

    sessions = repo.list_by_user(user_id)
    assert len(sessions) == 2
    assert all(item.revoked_at is not None for item in sessions)
    assert {item.revoke_reason for item in sessions} == {"security_test"}
