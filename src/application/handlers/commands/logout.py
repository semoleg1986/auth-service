from __future__ import annotations

from src.application.commands.logout import LogoutCommand
from src.application.errors import AuthenticationError
from src.application.ports.tokens import TokenService
from src.application.unit_of_work import UnitOfWork


def handle_logout(
    command: LogoutCommand,
    *,
    uow: UnitOfWork,
    token_service: TokenService,
) -> None:
    """
    Отозвать refresh токен (logout).

    :param command: Команда logout.
    :type command: LogoutCommand
    :param uow: Unit of Work для доступа к репозиториям.
    :type uow: UnitOfWork
    :param token_service: Сервис токенов.
    :type token_service: TokenService
    :raises AuthenticationError: Если refresh токен невалиден.
    :return: None
    :rtype: None
    """
    try:
        token_id, _ = token_service.decode_refresh_token(command.refresh_token)
    except Exception as exc:
        raise AuthenticationError("Invalid refresh token") from exc
    session = uow.session_repo.get_by_id(token_id)
    if session is None:
        raise AuthenticationError("Invalid refresh token")
    uow.session_repo.revoke(token_id)
    uow.commit()
