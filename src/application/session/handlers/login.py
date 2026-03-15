from __future__ import annotations

from datetime import timedelta
from typing import Protocol, runtime_checkable
from uuid import uuid4

from src.application.dtos.auth import AuthTokens, LoginResult
from src.application.errors import AuthenticationError
from src.application.ports.crypto import PasswordHasher
from src.application.ports.time import TimeProvider
from src.application.ports.tokens import TokenService
from src.application.session.commands.login import LoginCommand
from src.application.unit_of_work import UnitOfWork
from src.domain.access.policies import AccessPolicy
from src.domain.session.entity import Session


@runtime_checkable
class _PasswordHashUpgrader(Protocol):
    def upgrade_hash_if_needed(
        self, *, password: str, password_hash: str
    ) -> str | None:
        ...


def handle_login(
    command: LoginCommand,
    *,
    uow: UnitOfWork,
    password_hasher: PasswordHasher,
    token_service: TokenService,
    time_provider: TimeProvider,
    refresh_ttl_seconds: int,
    lock_threshold: int = 5,
    lock_ttl_seconds: int = 900,
) -> LoginResult:
    """
    Выполнить логин и выдать токены.

    :param command: Команда логина.
    :type command: LoginCommand
    :param uow: Unit of Work для доступа к репозиториям.
    :type uow: UnitOfWork
    :param password_hasher: Хешер паролей.
    :type password_hasher: PasswordHasher
    :param token_service: Сервис генерации токенов.
    :type token_service: TokenService
    :param time_provider: Провайдер времени.
    :type time_provider: TimeProvider
    :param refresh_ttl_seconds: TTL refresh токена в секундах.
    :type refresh_ttl_seconds: int
    :raises AuthenticationError: Если учетные данные неверны или аккаунт заблокирован.
    :return: Результат логина с токенами.
    :rtype: LoginResult
    """
    identifier = command.identifier.strip()
    account = uow.user_repo.get_by_email(identifier)
    if account is None:
        account = uow.user_repo.get_by_phone(identifier)
    if account is None:
        raise AuthenticationError("Invalid credentials")

    if not AccessPolicy.can_login(account):
        raise AuthenticationError("Account is blocked")

    now = time_provider.now()
    password_cred = account.get_password_credential()
    if password_cred is None or not password_cred.secret_hash:
        raise AuthenticationError("Invalid credentials")

    if account.is_password_locked(at=now):
        raise AuthenticationError("Credential is temporarily locked")

    if not password_hasher.verify(command.password, password_cred.secret_hash):
        account.register_failed_password_attempt(
            at=now,
            lock_threshold=lock_threshold,
            lock_ttl_seconds=lock_ttl_seconds,
        )
        uow.user_repo.save(account)
        uow.commit()
        if account.is_password_locked(at=now):
            raise AuthenticationError("Too many failed attempts. Try later")
        raise AuthenticationError("Invalid credentials")

    if isinstance(password_hasher, _PasswordHashUpgrader):
        upgraded_hash = password_hasher.upgrade_hash_if_needed(
            password=command.password,
            password_hash=password_cred.secret_hash,
        )
        if upgraded_hash is not None:
            account.replace_password_hash(
                new_secret_hash=upgraded_hash,
                at=now,
            )

    account.mark_login(at=now)
    account.register_successful_password_login(at=now)

    role_names = sorted([r.name for r in account.roles])
    access_token = token_service.issue_access_token(
        user_id=account.user_id, roles=role_names, org_id=account.org_id
    )

    session = Session(
        token_id=uuid4(),
        user_id=account.user_id,
        expires_at=now + timedelta(seconds=refresh_ttl_seconds),
        ip_address=command.ip_address,
        user_agent=command.user_agent,
        geo_city=command.geo_city,
        geo_region=command.geo_region,
        geo_country=command.geo_country,
        geo_display=command.geo_display,
    )
    uow.user_repo.save(account)
    uow.session_repo.save(session)

    refresh_token = token_service.issue_refresh_token(
        token_id=session.token_id, user_id=account.user_id
    )

    uow.commit()
    return LoginResult(
        user_id=str(account.user_id),
        tokens=AuthTokens(access_token=access_token, refresh_token=refresh_token),
    )
