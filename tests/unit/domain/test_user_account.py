from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.domain.access.role import ROLE_ADMIN, Role
from src.domain.errors import InvariantViolationError
from src.domain.identity.entity import UserAccount
from src.domain.identity.value_objects import AccountStatus, Credential


def test_user_account_requires_email_or_phone() -> None:
    with pytest.raises(InvariantViolationError, match="email or phone"):
        UserAccount(user_id=uuid4())


def test_user_account_accepts_email() -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    assert account.email == "user@example.com"
    assert account.phone is None


def test_user_account_accepts_phone() -> None:
    account = UserAccount(user_id=uuid4(), phone="+15550001122")
    assert account.phone == "+15550001122"
    assert account.email is None


def test_assign_and_remove_role() -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    role = Role(name=ROLE_ADMIN)
    account.assign_role(role)
    assert role in account.roles
    account.remove_role(role)
    assert role not in account.roles


def test_assign_unsupported_role_raises() -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    with pytest.raises(InvariantViolationError, match="Unsupported role"):
        account.assign_role(Role(name="methodist"))


def test_block_and_unblock() -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    account.block()
    assert account.status == AccountStatus.BLOCKED
    account.unblock()
    assert account.status == AccountStatus.ACTIVE


def test_add_password_credential() -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    cred = Credential(credential_id=uuid4(), type="password", secret_hash="hash")
    account.add_credential(cred)
    assert cred in account.credentials


def test_password_credential_requires_secret_hash() -> None:
    with pytest.raises(InvariantViolationError, match="requires secret_hash"):
        Credential(credential_id=uuid4(), type="password", secret_hash=None)


def test_password_credential_forbids_oauth_fields() -> None:
    with pytest.raises(InvariantViolationError, match="cannot have oauth provider"):
        Credential(
            credential_id=uuid4(),
            type="password",
            secret_hash="hash",
            provider="google",
        )


def test_add_oauth_credential() -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    cred = Credential(
        credential_id=uuid4(),
        type="oauth",
        provider="google",
        provider_user_id="123",
    )
    account.add_credential(cred)
    assert cred in account.credentials


def test_oauth_credential_requires_provider_fields() -> None:
    with pytest.raises(InvariantViolationError, match="requires provider"):
        Credential(
            credential_id=uuid4(),
            type="oauth",
            provider="google",
            provider_user_id=None,
        )


def test_oauth_credential_forbids_secret_hash() -> None:
    with pytest.raises(InvariantViolationError, match="cannot have secret_hash"):
        Credential(
            credential_id=uuid4(),
            type="oauth",
            provider="google",
            provider_user_id="42",
            secret_hash="hash",
        )


def test_add_unsupported_credential_type_raises() -> None:
    with pytest.raises(InvariantViolationError, match="Unsupported credential type"):
        Credential(credential_id=uuid4(), type="magic")


def test_add_duplicate_credential_type_raises() -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    account.add_credential(
        Credential(credential_id=uuid4(), type="password", secret_hash="hash")
    )
    with pytest.raises(InvariantViolationError, match="already exists"):
        account.add_credential(
            Credential(credential_id=uuid4(), type="password", secret_hash="hash2")
        )


def test_failed_password_attempt_increments_counter() -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    account.add_credential(
        Credential(credential_id=uuid4(), type="password", secret_hash="hash")
    )
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    account.register_failed_password_attempt(at=now)

    credential = account.get_password_credential()
    assert credential is not None
    assert credential.failed_attempts == 1
    assert credential.locked_until is None


def test_failed_password_attempt_locks_after_threshold() -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    account.add_credential(
        Credential(
            credential_id=uuid4(),
            type="password",
            secret_hash="hash",
            failed_attempts=4,
        )
    )
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    account.register_failed_password_attempt(
        at=now,
        lock_threshold=5,
        lock_ttl_seconds=600,
    )

    credential = account.get_password_credential()
    assert credential is not None
    assert credential.failed_attempts == 5
    assert credential.locked_until == datetime(2026, 1, 1, 0, 10, tzinfo=timezone.utc)
    assert account.is_password_locked(at=now) is True


def test_successful_password_login_resets_lock_and_counter() -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    account.add_credential(
        Credential(
            credential_id=uuid4(),
            type="password",
            secret_hash="hash",
            failed_attempts=3,
            locked_until=datetime(2026, 1, 1, 0, 5, tzinfo=timezone.utc),
        )
    )
    now = datetime(2026, 1, 1, 0, 1, tzinfo=timezone.utc)
    account.register_successful_password_login(at=now)

    credential = account.get_password_credential()
    assert credential is not None
    assert credential.failed_attempts == 0
    assert credential.locked_until is None
    assert credential.last_used_at == now
