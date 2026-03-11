from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.domain.aggregates.account import Session, UserAccount
from src.domain.policies.access_policy import AccessPolicy, Actor
from src.domain.value_objects import ROLE_AUDITOR, ROLE_SUPPORT, AccountStatus


def test_admin_can_assign_role() -> None:
    admin = Actor(user_id=uuid4(), is_admin=True)
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    assert AccessPolicy.can_assign_role(admin, account) is True


def test_user_cannot_assign_role() -> None:
    user = Actor(user_id=uuid4(), is_admin=False)
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    assert AccessPolicy.can_assign_role(user, account) is False


def test_actor_legacy_is_admin_populates_roles() -> None:
    admin = Actor(user_id=uuid4(), is_admin=True)
    assert admin.is_admin is True
    assert admin.has_role("admin") is True


def test_auditor_can_view_roles_and_sessions() -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    auditor = Actor(user_id=uuid4(), roles=frozenset({ROLE_AUDITOR}))
    assert AccessPolicy.can_view_roles(auditor, account) is True
    assert AccessPolicy.can_view_sessions(auditor, account) is True


def test_support_can_view_roles_and_sessions() -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    support = Actor(user_id=uuid4(), roles=frozenset({ROLE_SUPPORT}))
    assert AccessPolicy.can_view_roles(support, account) is True
    assert AccessPolicy.can_view_sessions(support, account) is True


def test_admin_can_block_user() -> None:
    admin = Actor(user_id=uuid4(), is_admin=True)
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    assert AccessPolicy.can_block_user(admin, account) is True


def test_can_login_requires_active() -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    assert AccessPolicy.can_login(account) is True
    account.status = AccountStatus.BLOCKED
    assert AccessPolicy.can_login(account) is False


def test_can_refresh_requires_active_session() -> None:
    now = datetime.now(timezone.utc)
    session = Session(
        token_id=uuid4(),
        user_id=uuid4(),
        expires_at=now + timedelta(minutes=5),
    )
    assert AccessPolicy.can_refresh(session, now=now) is True
    session.revoke(at=now)
    assert AccessPolicy.can_refresh(session, now=now) is False
