from __future__ import annotations

from src.application.access.commands.assign_role import AssignRoleCommand
from src.application.actor_context import ActorContext
from src.application.errors import (
    AccessDeniedError,
    InvariantViolationError,
    NotFoundError,
)
from src.application.unit_of_work import UnitOfWork
from src.domain.access.access_policy import AccessPolicy
from src.domain.access.role import Role
from src.domain.errors import InvariantViolationError as DomainInvariantError


def handle_assign_role(
    command: AssignRoleCommand,
    *,
    uow: UnitOfWork,
    actor: ActorContext,
) -> None:
    """
    Назначить роль пользователю (admin only).

    :param command: Команда назначения роли.
    :type command: AssignRoleCommand
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

    if not AccessPolicy.can_assign_role(actor.to_domain_actor(), account):
        raise AccessDeniedError("Access denied")

    try:
        account.assign_role(Role(name=command.role))
    except DomainInvariantError as exc:
        raise InvariantViolationError(str(exc)) from exc
    uow.user_repo.save(account)
    uow.commit()
