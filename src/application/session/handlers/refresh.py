from __future__ import annotations

from uuid import uuid4

from src.application.dtos.auth import AuthTokens
from src.application.errors import AuthenticationError
from src.application.ports.time import TimeProvider
from src.application.ports.tokens import TokenService
from src.application.session.commands.refresh import RefreshCommand
from src.application.unit_of_work import UnitOfWork
from src.domain.session import Session


def handle_refresh(
    command: RefreshCommand,
    *,
    uow: UnitOfWork,
    token_service: TokenService,
    time_provider: TimeProvider,
) -> AuthTokens:
    """
    Обновить access токен по refresh токену.

    :param command: Команда refresh.
    :type command: RefreshCommand
    :param uow: Unit of Work для доступа к репозиториям.
    :type uow: UnitOfWork
    :param token_service: Сервис токенов.
    :type token_service: TokenService
    :param time_provider: Провайдер времени.
    :type time_provider: TimeProvider
    :raises AuthenticationError: Если refresh токен невалиден/отозван.
    :return: Новые токены (access + исходный refresh).
    :rtype: AuthTokens
    """
    try:
        token_id, user_id = token_service.decode_refresh_token(command.refresh_token)
    except Exception as exc:
        raise AuthenticationError("Invalid refresh token") from exc
    session = uow.session_repo.get_by_id(token_id)
    if session is None or session.user_id != user_id:
        raise AuthenticationError("Invalid refresh token")

    now = time_provider.now()
    if session.revoked_at is not None:
        if session.revoke_reason == "rotated":
            uow.session_repo.revoke_all_by_user(
                user_id=user_id,
                reason="refresh_reuse_detected",
            )
            uow.commit()
            raise AuthenticationError("Refresh token reuse detected")
        raise AuthenticationError("Refresh token expired or revoked")
    if now >= session.expires_at:
        raise AuthenticationError("Refresh token expired or revoked")

    account = uow.user_repo.get_by_id(user_id)
    if account is None:
        raise AuthenticationError("Invalid refresh token")

    role_names = sorted([r.name for r in account.roles])
    access_token = token_service.issue_access_token(
        user_id=account.user_id, roles=role_names, org_id=account.org_id
    )
    session.revoke(at=now, reason="rotated")
    uow.session_repo.save(session)
    rotated_session = Session(
        token_id=uuid4(),
        user_id=user_id,
        expires_at=session.expires_at,
        ip_address=session.ip_address,
        user_agent=session.user_agent,
        geo_city=session.geo_city,
        geo_region=session.geo_region,
        geo_country=session.geo_country,
        geo_display=session.geo_display,
    )
    uow.session_repo.save(rotated_session)
    refresh_token = token_service.issue_refresh_token(
        token_id=rotated_session.token_id,
        user_id=user_id,
    )

    uow.commit()
    return AuthTokens(access_token=access_token, refresh_token=refresh_token)
