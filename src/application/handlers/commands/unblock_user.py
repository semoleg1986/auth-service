from __future__ import annotations

from src.application.commands.unblock_user import UnblockUserCommand
from src.application.errors import AccessDeniedError, NotFoundError
from src.application.unit_of_work import UnitOfWork
from src.domain.policies.access_policy import AccessPolicy, Actor


def handle_unblock_user(
    command: UnblockUserCommand,
    *,
    uow: UnitOfWork,
    actor: Actor,
) -> None:
    """
    Разблокировать пользователя (admin only).

    :param command: Команда разблокировки.
    :type command: UnblockUserCommand
    :param uow: Unit of Work.
    :type uow: UnitOfWork
    :param actor: Актор (должен быть admin).
    :type actor: Actor
    :raises NotFoundError: Если пользователь не найден.
    :raises AccessDeniedError: Если доступ запрещён.
    :return: None
    :rtype: None
    """
    account = uow.user_repo.get_by_id(command.user_id)
    if account is None:
        raise NotFoundError("User not found")

    if not AccessPolicy.can_unblock_user(actor, account):
        raise AccessDeniedError("Access denied")

    account.unblock()
    uow.user_repo.save(account)
    uow.commit()
