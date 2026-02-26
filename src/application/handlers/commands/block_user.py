from __future__ import annotations

from src.application.commands.block_user import BlockUserCommand
from src.application.errors import AccessDeniedError, NotFoundError
from src.application.unit_of_work import UnitOfWork
from src.domain.policies.access_policy import AccessPolicy, Actor


def handle_block_user(
    command: BlockUserCommand,
    *,
    uow: UnitOfWork,
    actor: Actor,
) -> None:
    """
    Заблокировать пользователя (admin only).

    :param command: Команда блокировки.
    :type command: BlockUserCommand
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

    if not AccessPolicy.can_block_user(actor, account):
        raise AccessDeniedError("Access denied")

    account.block()
    uow.user_repo.save(account)
    uow.commit()
