from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest

from src.application.commands import (
    AssignRoleCommand,
    BlockUserCommand,
    LoginCommand,
    LogoutCommand,
    RefreshCommand,
    RegisterCommand,
    UnblockUserCommand,
)
from src.application.dtos.auth import AuthTokens
from src.application.errors import (
    AccessDeniedError,
    AuthenticationError,
    InvariantViolationError,
)
from src.application.handlers import (
    handle_assign_role,
    handle_block_user,
    handle_list_role_assignments,
    handle_list_sessions,
    handle_login,
    handle_logout,
    handle_refresh,
    handle_register,
    handle_unblock_user,
)
from src.application.ports.crypto import PasswordHasher
from src.application.ports.time import TimeProvider
from src.application.ports.tokens import TokenService
from src.application.queries import ListRoleAssignmentsQuery, ListSessionsQuery
from src.application.unit_of_work import UnitOfWork
from src.domain.aggregates.account import Credential, Session, UserAccount
from src.domain.policies.access_policy import Actor
from src.domain.value_objects import AccountStatus, Role


@dataclass
class InMemoryUserRepo:
    users: dict[UUID, UserAccount]

    def get_by_id(self, user_id: UUID) -> UserAccount | None:
        return self.users.get(user_id)

    def get_by_email(self, email: str) -> UserAccount | None:
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    def get_by_phone(self, phone: str) -> UserAccount | None:
        for user in self.users.values():
            if user.phone == phone:
                return user
        return None

    def save(self, account: UserAccount) -> None:
        self.users[account.user_id] = account


@dataclass
class InMemorySessionRepo:
    sessions: dict[UUID, Session]

    def get_by_id(self, token_id: UUID) -> Session | None:
        return self.sessions.get(token_id)

    def save(self, session: Session) -> None:
        self.sessions[session.token_id] = session

    def revoke(self, token_id: UUID) -> None:
        session = self.sessions.get(token_id)
        if session is not None:
            session.revoked_at = datetime.now(timezone.utc)

    def list_by_user(self, user_id: UUID) -> list[Session]:
        return [s for s in self.sessions.values() if s.user_id == user_id]


class InMemoryUoW(UnitOfWork):
    def __init__(
        self, user_repo: InMemoryUserRepo, session_repo: InMemorySessionRepo
    ) -> None:
        self.user_repo = user_repo
        self.session_repo = session_repo
        self.committed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.committed = False


class SimpleHasher(PasswordHasher):
    def hash(self, password: str) -> str:
        return f"hash:{password}"

    def verify(self, password: str, password_hash: str) -> bool:
        return password_hash == f"hash:{password}"


class FixedTime(TimeProvider):
    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


class SimpleTokenService(TokenService):
    def issue_access_token(self, *, user_id: UUID, roles: list[str]) -> str:
        return f"access:{user_id}:{','.join(roles)}"

    def issue_refresh_token(self, *, token_id: UUID, user_id: UUID) -> str:
        return f"refresh:{token_id}:{user_id}"

    def decode_refresh_token(self, refresh_token: str) -> tuple[UUID, UUID]:
        prefix, token_id, user_id = refresh_token.split(":", 2)
        if prefix != "refresh":
            raise ValueError("Invalid refresh token")
        return UUID(token_id), UUID(user_id)


@pytest.fixture()
def user_repo() -> InMemoryUserRepo:
    return InMemoryUserRepo(users={})


@pytest.fixture()
def session_repo() -> InMemorySessionRepo:
    return InMemorySessionRepo(sessions={})


@pytest.fixture()
def uow(user_repo: InMemoryUserRepo, session_repo: InMemorySessionRepo) -> InMemoryUoW:
    return InMemoryUoW(user_repo, session_repo)


@pytest.fixture()
def hasher() -> SimpleHasher:
    return SimpleHasher()


@pytest.fixture()
def tokens() -> SimpleTokenService:
    return SimpleTokenService()


@pytest.fixture()
def now() -> datetime:
    return datetime(2024, 1, 1, tzinfo=timezone.utc)


@pytest.fixture()
def time_provider(now: datetime) -> FixedTime:
    return FixedTime(now)


def test_register_success(uow: InMemoryUoW, hasher: SimpleHasher) -> None:
    account = handle_register(
        RegisterCommand(email="user@example.com", phone=None, password="pass"),
        uow=uow,
        password_hasher=hasher,
    )
    assert account.email == "user@example.com"
    assert any(c.type == "password" for c in account.credentials)
    assert Role(name="user") in account.roles
    assert uow.committed is True


def test_register_bootstrap_admin_email(
    uow: InMemoryUoW, hasher: SimpleHasher, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("BOOTSTRAP_ADMIN_EMAIL", "admin@example.com")
    account = handle_register(
        RegisterCommand(email="admin@example.com", phone=None, password="pass"),
        uow=uow,
        password_hasher=hasher,
    )
    assert Role(name="admin") in account.roles


def test_register_duplicate_email_raises(
    uow: InMemoryUoW, hasher: SimpleHasher
) -> None:
    handle_register(
        RegisterCommand(email="user@example.com", phone=None, password="pass"),
        uow=uow,
        password_hasher=hasher,
    )
    with pytest.raises(InvariantViolationError):
        handle_register(
            RegisterCommand(email="user@example.com", phone=None, password="pass2"),
            uow=uow,
            password_hasher=hasher,
        )


def test_login_success(
    uow: InMemoryUoW,
    hasher: SimpleHasher,
    tokens: SimpleTokenService,
    time_provider: FixedTime,
) -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    account.add_credential(
        Credential(
            credential_id=uuid4(), type="password", secret_hash=hasher.hash("pass")
        )
    )
    account.assign_role(Role(name="user"))
    uow.user_repo.save(account)

    result = handle_login(
        LoginCommand(identifier="user@example.com", password="pass"),
        uow=uow,
        password_hasher=hasher,
        token_service=tokens,
        time_provider=time_provider,
        refresh_ttl_seconds=3600,
    )

    assert result.user_id == str(account.user_id)
    assert result.tokens.access_token.startswith("access:")
    assert result.tokens.refresh_token.startswith("refresh:")
    assert uow.committed is True


def test_login_invalid_password_raises(
    uow: InMemoryUoW,
    hasher: SimpleHasher,
    tokens: SimpleTokenService,
    time_provider: FixedTime,
) -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    account.add_credential(
        Credential(
            credential_id=uuid4(), type="password", secret_hash=hasher.hash("pass")
        )
    )
    uow.user_repo.save(account)

    with pytest.raises(AuthenticationError):
        handle_login(
            LoginCommand(identifier="user@example.com", password="wrong"),
            uow=uow,
            password_hasher=hasher,
            token_service=tokens,
            time_provider=time_provider,
            refresh_ttl_seconds=3600,
        )


def test_login_blocked_raises(
    uow: InMemoryUoW,
    hasher: SimpleHasher,
    tokens: SimpleTokenService,
    time_provider: FixedTime,
) -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    account.status = AccountStatus.BLOCKED
    account.add_credential(
        Credential(
            credential_id=uuid4(), type="password", secret_hash=hasher.hash("pass")
        )
    )
    uow.user_repo.save(account)

    with pytest.raises(AuthenticationError):
        handle_login(
            LoginCommand(identifier="user@example.com", password="pass"),
            uow=uow,
            password_hasher=hasher,
            token_service=tokens,
            time_provider=time_provider,
            refresh_ttl_seconds=3600,
        )


def test_refresh_success(
    uow: InMemoryUoW,
    tokens: SimpleTokenService,
    time_provider: FixedTime,
    now: datetime,
) -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    account.assign_role(Role(name="user"))
    uow.user_repo.save(account)

    session = Session(
        token_id=uuid4(), user_id=account.user_id, expires_at=now + timedelta(minutes=5)
    )
    uow.session_repo.save(session)
    refresh_token = tokens.issue_refresh_token(
        token_id=session.token_id, user_id=account.user_id
    )

    tokens_out = handle_refresh(
        RefreshCommand(refresh_token=refresh_token),
        uow=uow,
        token_service=tokens,
        time_provider=time_provider,
    )

    assert isinstance(tokens_out, AuthTokens)
    assert tokens_out.access_token.startswith("access:")
    assert tokens_out.refresh_token == refresh_token


def test_refresh_invalid_token_raises(
    uow: InMemoryUoW, tokens: SimpleTokenService, time_provider: FixedTime
) -> None:
    with pytest.raises(AuthenticationError):
        handle_refresh(
            RefreshCommand(refresh_token="badtoken"),
            uow=uow,
            token_service=tokens,
            time_provider=time_provider,
        )


def test_logout_revokes_session(
    uow: InMemoryUoW, tokens: SimpleTokenService, now: datetime
) -> None:
    session = Session(
        token_id=uuid4(), user_id=uuid4(), expires_at=now + timedelta(minutes=5)
    )
    uow.session_repo.save(session)
    refresh_token = tokens.issue_refresh_token(
        token_id=session.token_id, user_id=session.user_id
    )

    handle_logout(
        LogoutCommand(refresh_token=refresh_token), uow=uow, token_service=tokens
    )
    assert uow.session_repo.get_by_id(session.token_id).revoked_at is not None
    assert uow.committed is True


def test_assign_role_admin_only(uow: InMemoryUoW) -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    uow.user_repo.save(account)

    admin = Actor(user_id=uuid4(), is_admin=True)
    handle_assign_role(
        AssignRoleCommand(user_id=account.user_id, role="admin"),
        uow=uow,
        actor=admin,
    )
    assert Role(name="admin") in account.roles

    user = Actor(user_id=uuid4(), is_admin=False)
    with pytest.raises(AccessDeniedError):
        handle_assign_role(
            AssignRoleCommand(user_id=account.user_id, role="mod"),
            uow=uow,
            actor=user,
        )


def test_block_and_unblock_admin_only(uow: InMemoryUoW) -> None:
    account = UserAccount(user_id=uuid4(), email="user@example.com")
    uow.user_repo.save(account)

    user = Actor(user_id=uuid4(), is_admin=False)
    with pytest.raises(AccessDeniedError):
        handle_block_user(
            BlockUserCommand(user_id=account.user_id), uow=uow, actor=user
        )

    admin = Actor(user_id=uuid4(), is_admin=True)
    handle_block_user(BlockUserCommand(user_id=account.user_id), uow=uow, actor=admin)
    assert account.status == AccountStatus.BLOCKED

    handle_unblock_user(
        UnblockUserCommand(user_id=account.user_id), uow=uow, actor=admin
    )
    assert account.status == AccountStatus.ACTIVE


def test_list_sessions_admin_or_self(uow: InMemoryUoW, now: datetime) -> None:
    user_id = uuid4()
    account = UserAccount(user_id=user_id, email="user@example.com")
    uow.user_repo.save(account)

    s1 = Session(
        token_id=uuid4(),
        user_id=user_id,
        expires_at=now + timedelta(minutes=5),
    )
    s2 = Session(
        token_id=uuid4(),
        user_id=user_id,
        expires_at=now + timedelta(minutes=10),
    )
    uow.session_repo.save(s1)
    uow.session_repo.save(s2)

    admin = Actor(user_id=uuid4(), is_admin=True)
    self_actor = Actor(user_id=user_id, is_admin=False)

    sessions_admin = handle_list_sessions(
        ListSessionsQuery(user_id=user_id), uow=uow, actor=admin
    )
    sessions_self = handle_list_sessions(
        ListSessionsQuery(user_id=user_id), uow=uow, actor=self_actor
    )

    assert {s.token_id for s in sessions_admin} == {s1.token_id, s2.token_id}
    assert {s.token_id for s in sessions_self} == {s1.token_id, s2.token_id}


def test_list_sessions_denied(uow: InMemoryUoW) -> None:
    user_id = uuid4()
    account = UserAccount(user_id=user_id, email="user@example.com")
    uow.user_repo.save(account)

    other = Actor(user_id=uuid4(), is_admin=False)
    with pytest.raises(AccessDeniedError):
        handle_list_sessions(ListSessionsQuery(user_id=user_id), uow=uow, actor=other)


def test_list_role_assignments_admin_or_self(uow: InMemoryUoW) -> None:
    user_id = uuid4()
    account = UserAccount(user_id=user_id, email="user@example.com")
    account.assign_role(Role("user"))
    account.assign_role(Role("admin"))
    uow.user_repo.save(account)

    admin = Actor(user_id=uuid4(), is_admin=True)
    self_actor = Actor(user_id=user_id, is_admin=False)

    roles_admin = handle_list_role_assignments(
        ListRoleAssignmentsQuery(user_id=user_id), uow=uow, actor=admin
    )
    roles_self = handle_list_role_assignments(
        ListRoleAssignmentsQuery(user_id=user_id), uow=uow, actor=self_actor
    )

    assert {r.name for r in roles_admin} == {"user", "admin"}
    assert {r.name for r in roles_self} == {"user", "admin"}


def test_list_role_assignments_denied(uow: InMemoryUoW) -> None:
    user_id = uuid4()
    account = UserAccount(user_id=user_id, email="user@example.com")
    uow.user_repo.save(account)

    other = Actor(user_id=uuid4(), is_admin=False)
    with pytest.raises(AccessDeniedError):
        handle_list_role_assignments(
            ListRoleAssignmentsQuery(user_id=user_id), uow=uow, actor=other
        )
