from __future__ import annotations

from src.application.actor_context import ActorContext
from src.application.errors import AccessDeniedError, NotFoundError
from src.application.identity.commands.unblock_user import UnblockUserCommand
from src.application.unit_of_work import UnitOfWork
from src.domain.access.policies import AccessPolicy


def handle_unblock_user(
    command: UnblockUserCommand,
    *,
    uow: UnitOfWork,
    actor: ActorContext,
) -> None:
    """
    Разблокировать пользователя (admin only).

    :param command: Команда разблокировки.
    :type command: UnblockUserCommand
    :param uow: Unit of Work.
    :type uow: UnitOfWork
    :param actor: Актор (должен быть admin).
    :type actor: ActorContext
    :raises NotFoundError: Если пользователь не найден.
    :raises AccessDeniedError: Если доступ запрещён.
    :return: None
    :rtype: None
    """
    account = uow.user_repo.get_by_id(command.user_id)
    if account is None:
        raise NotFoundError("User not found")

    if not AccessPolicy.can_unblock_user(actor.to_domain_actor(), account):
        raise AccessDeniedError("Access denied")

    account.unblock()
    uow.user_repo.save(account)
    uow.commit()
