from __future__ import annotations

from uuid import uuid4

import pytest

from src.domain.aggregates.account import Credential, UserAccount
from src.domain.errors import InvariantViolationError
from src.domain.value_objects import AccountStatus, Role


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
    role = Role(name="admin")
    account.assign_role(role)
    assert role in account.roles
    account.remove_role(role)
    assert role not in account.roles


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


def test_add_unsupported_credential_type_raises() -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    cred = Credential(credential_id=uuid4(), type="magic")
    with pytest.raises(InvariantViolationError, match="Unsupported credential type"):
        account.add_credential(cred)


def test_add_duplicate_credential_type_raises() -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    account.add_credential(
        Credential(credential_id=uuid4(), type="password", secret_hash="hash")
    )
    with pytest.raises(InvariantViolationError, match="already exists"):
        account.add_credential(
            Credential(credential_id=uuid4(), type="password", secret_hash="hash2")
        )
