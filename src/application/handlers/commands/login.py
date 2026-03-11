from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from src.application.commands.login import LoginCommand
from src.application.dtos.auth import AuthTokens, LoginResult
from src.application.errors import AuthenticationError
from src.application.ports.crypto import PasswordHasher
from src.application.ports.time import TimeProvider
from src.application.ports.tokens import TokenService
from src.application.unit_of_work import UnitOfWork
from src.domain.aggregates.account import Session
from src.domain.policies.access_policy import AccessPolicy


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
